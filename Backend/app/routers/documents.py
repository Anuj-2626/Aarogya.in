from datetime import datetime
from pathlib import Path
from uuid import uuid4
import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import MedicalDocument, Session as SessionModel
from ..schemas import (
    MedicalDocumentDetailResponse,
    MedicalDocumentResponse
)
from ..services.document_extraction_service import (
    document_extraction_service
)
from ..services.ocr_service import ocr_service
from ..services.timeline_service import create_timeline_event


router = APIRouter(
    prefix="/documents",
    tags=["Medical Documents"]
)


UPLOAD_DIRECTORY = Path("uploads/medical_documents")

ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def build_document_detail(
    document: MedicalDocument
) -> MedicalDocumentDetailResponse:

    structured_data = None

    if document.extracted_data:
        try:
            structured_data = json.loads(
                document.extracted_data
            )
        except json.JSONDecodeError:
            structured_data = None

    return MedicalDocumentDetailResponse(
        document_id=document.document_id,
        session_id=document.session_id,
        filename=document.filename,
        file_type=document.file_type,
        ocr_status=document.ocr_status,
        ocr_text=document.ocr_text,
        extracted_data=structured_data,
        document_date=document.document_date,
        created_at=document.created_at
    )


def parse_document_date(
    dates: list[str]
) -> datetime | None:

    if not dates:
        return None

    date_formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d %B %Y"
    ]

    for date_value in dates:
        for date_format in date_formats:
            try:
                return datetime.strptime(
                    date_value,
                    date_format
                )
            except ValueError:
                continue

    return None


def create_document_timeline_events(
    db: Session,
    document: MedicalDocument,
    session: SessionModel,
    structured_data: dict
):
    event_date = parse_document_date(
        structured_data.get("dates", [])
    )

    extracted_categories = [
        ("diagnoses", "diagnosis", "Diagnosis"),
        ("medications", "medication", "Medication"),
        ("lab_results", "lab_result", "Lab Result"),
        ("procedures", "procedure", "Procedure")
    ]

    for field_name, event_type, title_prefix in extracted_categories:
        values = structured_data.get(
            field_name,
            []
        )

        for value in values:
            create_timeline_event(
                db=db,
                patient_id=session.patient_id,
                session_id=session.session_id,
                event_date=event_date,
                event_type=event_type,
                title=f"{title_prefix}: {value}",
                description=(
                    f"Extracted from medical document "
                    f"'{document.filename}'."
                ),
                source_type="document",
                source_id=document.document_id,
                structured_data=json.dumps(
                    {
                        "document_id": document.document_id,
                        "filename": document.filename,
                        "field": field_name,
                        "value": value
                    },
                    ensure_ascii=False
                )
            )


@router.post(
    "/upload",
    response_model=MedicalDocumentResponse,
    status_code=201
)
async def upload_medical_document(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported medical document file type"
        )

    file_extension = ALLOWED_FILE_TYPES[file.content_type]

    original_name = Path(
        file.filename or "document"
    ).name

    unique_filename = (
        f"{uuid4().hex}_{original_name}"
    )

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = UPLOAD_DIRECTORY / unique_filename

    file_size = 0

    try:
        with file_path.open("wb") as destination:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Medical document exceeds 10 MB limit"
                    )

                destination.write(chunk)

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as error:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to store medical document"
        ) from error

    document = MedicalDocument(
        session_id=session_id,
        filename=original_name,
        file_type=file_extension,
        storage_path=str(file_path),
        ocr_status="pending"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.post(
    "/{document_id}/process",
    response_model=MedicalDocumentDetailResponse
)
def process_medical_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(MedicalDocument).filter(
        MedicalDocument.document_id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Medical document not found"
        )

    session = db.query(SessionModel).filter(
        SessionModel.session_id == document.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    document.ocr_status = "processing"
    db.commit()

    try:
        extracted_text = ocr_service.extract_text(
            file_path=document.storage_path,
            file_type=document.file_type,
            language_code=session.language
        )

        document.ocr_text = extracted_text

        structured_data = (
            document_extraction_service.extract(
                extracted_text
            )
        )

        document.extracted_data = json.dumps(
            structured_data,
            ensure_ascii=False
        )

        document.ocr_status = "completed"

        db.commit()

        create_document_timeline_events(
            db=db,
            document=document,
            session=session,
            structured_data=structured_data
        )

        db.refresh(document)

        return build_document_detail(document)

    except Exception as error:
        document.ocr_status = "failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        ) from error


@router.get(
    "/session/{session_id}",
    response_model=list[MedicalDocumentResponse]
)
def get_session_documents(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return db.query(MedicalDocument).filter(
        MedicalDocument.session_id == session_id
    ).order_by(
        MedicalDocument.created_at
    ).all()


@router.get(
    "/{document_id}",
    response_model=MedicalDocumentDetailResponse
)
def get_medical_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(MedicalDocument).filter(
        MedicalDocument.document_id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Medical document not found"
        )

    return build_document_detail(document)