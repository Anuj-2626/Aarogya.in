import io
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from Backend.app.models import MedicalDocument, TimelineEvent


def create_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Document Test Patient",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "phone": "9999999999",
            "preferred_language": "en"
        }
    )

    assert response.status_code == 201

    return response.json()["patient_id"]


def create_session(client, patient_id):
    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "session_type": "clinical_intake",
            "language": "en"
        }
    )

    assert response.status_code == 201

    return response.json()["session_id"]


def upload_document(
    client,
    session_id,
    filename="report.pdf",
    content_type="application/pdf",
    content=b"Sample medical document"
):
    return client.post(
        "/documents/upload",
        params={"session_id": session_id},
        files={
            "file": (
                filename,
                io.BytesIO(content),
                content_type
            )
        }
    )


def test_upload_pdf_document(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    response = upload_document(
        client,
        session_id
    )

    assert response.status_code == 201

    data = response.json()

    assert data["session_id"] == session_id
    assert data["filename"] == "report.pdf"
    assert data["file_type"] == "pdf"
    assert data["ocr_status"] == "pending"
    assert data["storage_path"]


def test_upload_jpeg_document(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    response = upload_document(
        client,
        session_id,
        filename="report.jpg",
        content_type="image/jpeg",
        content=b"fake jpeg content"
    )

    assert response.status_code == 201

    data = response.json()

    assert data["file_type"] == "jpg"
    assert data["ocr_status"] == "pending"


def test_upload_png_document(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    response = upload_document(
        client,
        session_id,
        filename="report.png",
        content_type="image/png",
        content=b"fake png content"
    )

    assert response.status_code == 201

    data = response.json()

    assert data["file_type"] == "png"


def test_upload_docx_document(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    response = upload_document(
        client,
        session_id,
        filename="report.docx",
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        content=b"fake docx content"
    )

    assert response.status_code == 201

    data = response.json()

    assert data["file_type"] == "docx"


def test_upload_rejects_unsupported_file_type(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    response = upload_document(
        client,
        session_id,
        filename="report.txt",
        content_type="text/plain",
        content=b"plain text"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported medical document file type"
    )


def test_upload_rejects_nonexistent_session(client):
    response = upload_document(
        client,
        session_id=999999
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_upload_sanitizes_filename(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    response = upload_document(
        client,
        session_id,
        filename="../../secret_report.pdf"
    )

    assert response.status_code == 201

    data = response.json()

    assert data["filename"] == "secret_report.pdf"
    assert ".." not in Path(data["filename"]).parts


def test_get_session_documents(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    upload_response = upload_document(
        client,
        session_id
    )

    assert upload_response.status_code == 201

    response = client.get(
        f"/documents/session/{session_id}"
    )

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 1
    assert documents[0]["filename"] == "report.pdf"


def test_get_session_documents_rejects_nonexistent_session(client):
    response = client.get(
        "/documents/session/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_get_document(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    upload_response = upload_document(
        client,
        session_id
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["document_id"]

    response = client.get(
        f"/documents/{document_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_id
    assert data["session_id"] == session_id
    assert data["ocr_status"] == "pending"


def test_get_nonexistent_document(client):
    response = client.get(
        "/documents/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Medical document not found"
    )


def test_process_document_success(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    upload_response = upload_document(
        client,
        session_id
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["document_id"]

    extracted_text = (
        "Patient has diabetes.\n"
        "Medication: Metformin.\n"
        "Lab Result: HbA1c 7.2.\n"
        "Procedure: Blood test.\n"
        "Date: 12/08/2026"
    )

    structured_data = {
        "dates": ["12/08/2026"],
        "diagnoses": ["Diabetes"],
        "medications": ["Metformin"],
        "lab_results": ["HbA1c 7.2"],
        "procedures": ["Blood test"]
    }

    with patch(
        "Backend.app.routers.documents.ocr_service.extract_text",
        return_value=extracted_text
    ), patch(
        "Backend.app.routers.documents.document_extraction_service.extract",
        return_value=structured_data
    ):
        response = client.post(
            f"/documents/{document_id}/process"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_id
    assert data["ocr_status"] == "completed"
    assert data["ocr_text"] == extracted_text
    assert data["extracted_data"] == structured_data
    assert data["document_date"] is None


def test_process_document_creates_timeline_events(
    client,
    db_session
):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    upload_response = upload_document(
        client,
        session_id
    )

    document_id = upload_response.json()["document_id"]

    structured_data = {
        "dates": ["12/08/2026"],
        "diagnoses": ["Diabetes"],
        "medications": ["Metformin"],
        "lab_results": ["HbA1c 7.2"],
        "procedures": ["Blood test"]
    }

    with patch(
        "Backend.app.routers.documents.ocr_service.extract_text",
        return_value="Medical report text"
    ), patch(
        "Backend.app.routers.documents.document_extraction_service.extract",
        return_value=structured_data
    ):
        response = client.post(
            f"/documents/{document_id}/process"
        )

    assert response.status_code == 200

    events = db_session.query(TimelineEvent).filter(
        TimelineEvent.source_type == "document",
        TimelineEvent.source_id == document_id
    ).all()

    assert len(events) == 4

    event_types = {
        event.event_type
        for event in events
    }

    assert event_types == {
        "diagnosis",
        "medication",
        "lab_result",
        "procedure"
    }


def test_process_document_nonexistent_document(client):
    response = client.post(
        "/documents/999999/process"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Medical document not found"
    )


def test_process_document_ocr_failure(
    client,
    db_session
):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    upload_response = upload_document(
        client,
        session_id
    )

    document_id = upload_response.json()["document_id"]

    with patch(
        "Backend.app.routers.documents.ocr_service.extract_text",
        side_effect=RuntimeError("OCR engine failed")
    ):
        response = client.post(
            f"/documents/{document_id}/process"
        )

    assert response.status_code == 500
    assert "Document processing failed" in (
        response.json()["detail"]
    )

    document = db_session.query(MedicalDocument).filter(
        MedicalDocument.document_id == document_id
    ).first()

    assert document is not None
    assert document.ocr_status == "failed"


def test_process_document_extraction_failure(client):
    patient_id = create_patient(client)
    session_id = create_session(client, patient_id)

    upload_response = upload_document(
        client,
        session_id
    )

    document_id = upload_response.json()["document_id"]

    with patch(
        "Backend.app.routers.documents.ocr_service.extract_text",
        return_value="OCR text"
    ), patch(
        "Backend.app.routers.documents.document_extraction_service.extract",
        side_effect=RuntimeError("Extraction failed")
    ):
        response = client.post(
            f"/documents/{document_id}/process"
        )

    assert response.status_code == 500
    assert "Document processing failed" in (
        response.json()["detail"]
    )


def test_build_document_detail_handles_invalid_json(
    db_session
):
    document = MedicalDocument(
        session_id=1,
        filename="invalid.pdf",
        file_type="pdf",
        storage_path="uploads/invalid.pdf",
        ocr_status="completed",
        ocr_text="text",
        extracted_data="{invalid json"
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    from Backend.app.routers.documents import build_document_detail

    result = build_document_detail(document)

    assert result.extracted_data is None


def test_parse_document_date():
    from Backend.app.routers.documents import parse_document_date

    result = parse_document_date(
        ["12/08/2026"]
    )

    assert result == datetime(2026, 8, 12)


def test_parse_document_date_supports_multiple_formats():
    from Backend.app.routers.documents import parse_document_date

    formats_and_expected = [
        ("12-08-2026", datetime(2026, 8, 12)),
        ("12/08/26", datetime(2026, 8, 12)),
        ("12-08-26", datetime(2026, 8, 12)),
        ("2026/08/12", datetime(2026, 8, 12)),
        ("2026-08-12", datetime(2026, 8, 12)),
        ("12 August 2026", datetime(2026, 8, 12)),
    ]

    for date_value, expected in formats_and_expected:
        result = parse_document_date(
            [date_value]
        )

        assert result == expected


def test_parse_document_date_returns_none_when_missing():
    from Backend.app.routers.documents import parse_document_date

    assert parse_document_date([]) is None


def test_parse_document_date_returns_none_for_invalid_date():
    from Backend.app.routers.documents import parse_document_date

    assert parse_document_date(
        ["not-a-date"]
    ) is None