from datetime import datetime, timezone
import json

from sqlalchemy.orm import Session

from ..models import (
    Answer,
    ClinicalSummary,
    Interview,
    MedicalDocument,
    Patient,
    Question,
    Session as SessionModel,
    TimelineEvent,
)

from ..schemas import (
    FHIRAllergyIntolerance,
    FHIRBundle,
    FHIRBundleEntry,
    FHIRCodeableConcept,
    FHIRComposition,
    FHIRCondition,
    FHIRDiagnosticReport,
    FHIRDocumentReference,
    FHIREncounter,
    FHIRIdentifier,
    FHIRMedicationStatement,
    FHIRMeta,
    FHIRObservation,
    FHIRPatient,
    FHIRPeriod,
    FHIRQuestionnaireResponse,
    FHIRQuestionnaireResponseItem,
    FHIRReference,
)


FHIR_BASE_URL = "urn:sih-project"


def _resource_id(resource_type: str, identifier: int) -> str:
    return f"{resource_type.lower()}-{identifier}"


def _patient_reference(patient_id: int) -> FHIRReference:
    return FHIRReference(
        reference=f"Patient/{_resource_id('Patient', patient_id)}"
    )


def _encounter_reference(session_id: int) -> FHIRReference:
    return FHIRReference(
        reference=f"Encounter/{_resource_id('Encounter', session_id)}"
    )


def _build_meta(resource_name: str) -> FHIRMeta:
    return FHIRMeta(
        profile=[
            f"{FHIR_BASE_URL}/StructureDefinition/{resource_name}"
        ]
    )


def _codeable_concept(
    text: str | None,
) -> FHIRCodeableConcept:
    return FHIRCodeableConcept(
        text=text.strip() if text else None
    )


def map_patient_to_fhir(
    patient: Patient,
) -> FHIRPatient:

    birth_date = None

    if patient.date_of_birth:
        birth_date = patient.date_of_birth.date().isoformat()

    return FHIRPatient(
        id=_resource_id(
            "Patient",
            patient.patient_id,
        ),
        meta=_build_meta("Patient"),
        identifier=[
            FHIRIdentifier(
                system=f"{FHIR_BASE_URL}/patient-id",
                value=str(patient.patient_id),
            )
        ],
        name=[
            {
                "text": patient.name,
            }
        ],
        birthDate=birth_date,
        gender=patient.gender,
        telecom=(
            [
                {
                    "system": "phone",
                    "value": patient.phone,
                    "use": "mobile",
                }
            ]
            if patient.phone
            else []
        ),
    )


def map_session_to_fhir(
    clinical_session: SessionModel,
) -> FHIREncounter:

    return FHIREncounter(
        id=_resource_id(
            "Encounter",
            clinical_session.session_id,
        ),
        meta=_build_meta("Encounter"),
        identifier=[
            FHIRIdentifier(
                system=f"{FHIR_BASE_URL}/session-id",
                value=str(
                    clinical_session.session_id
                ),
            )
        ],
        status=(
            clinical_session.status
            if clinical_session.status
            else "unknown"
        ),
        encounter_class={
            "system": f"{FHIR_BASE_URL}/encounter-class",
            "code": "OPD",
            "display": "Outpatient Department",
        },
        subject=_patient_reference(
            clinical_session.patient_id
        ),
        period=FHIRPeriod(
            start=clinical_session.started_at,
            end=clinical_session.completed_at,
        ),
    )


def map_interview_to_fhir(
    db: Session,
    interview: Interview,
) -> FHIRQuestionnaireResponse:

    answers = (
        db.query(
            Answer,
            Question,
        )
        .join(
            Question,
            Answer.question_id
            == Question.question_id,
        )
        .filter(
            Answer.interview_id
            == interview.interview_id
        )
        .order_by(
            Question.sequence_number.asc(),
            Answer.answer_id.asc(),
        )
        .all()
    )

    items = []

    for answer, question in answers:

        items.append(
            FHIRQuestionnaireResponseItem(
                linkId=question.question_code,
                text=question.question_text,
                answer=[
                    {
                        "valueString":
                        answer.answer_text
                    }
                ],
            )
        )

    return FHIRQuestionnaireResponse(
        id=_resource_id(
            "QuestionnaireResponse",
            interview.interview_id,
        ),
        meta=_build_meta(
            "QuestionnaireResponse"
        ),
        status="completed",
        subject=_patient_reference(
            interview.session.patient_id
        ),
        encounter=_encounter_reference(
            interview.session_id
        ),
        authored=(
            interview.created_at
            if interview.created_at
            else datetime.now(timezone.utc)
        ),
        item=items,
    )


def map_timeline_event_to_observation(
    event: TimelineEvent,
) -> FHIRObservation:

    return FHIRObservation(
        id=_resource_id(
            "Observation",
            event.event_id,
        ),
        meta=_build_meta("Observation"),
        status="final",
        code=_codeable_concept(
            event.title
        ),
        subject=_patient_reference(
            event.patient_id
        ),
        encounter=(
            _encounter_reference(
                event.session_id
            )
            if event.session_id
            else None
        ),
        effectiveDateTime=event.event_date,
        valueString=event.description,
        note=[
            {
                "text": (
                    f"Source: {event.source_type}"
                    + (
                        f" ({event.source_id})"
                        if event.source_id is not None
                        else ""
                    )
                )
            }
        ],
    )


def map_diagnosis_to_condition(
    event: TimelineEvent,
) -> FHIRCondition:

    return FHIRCondition(
        id=_resource_id(
            "Condition",
            event.event_id,
        ),
        meta=_build_meta("Condition"),
        clinicalStatus=FHIRCodeableConcept(
            text="active"
        ),
        verificationStatus=FHIRCodeableConcept(
            text="reported"
        ),
        code=_codeable_concept(
            event.title
        ),
        subject=_patient_reference(
            event.patient_id
        ),
        encounter=(
            _encounter_reference(
                event.session_id
            )
            if event.session_id
            else None
        ),
        recordedDate=event.created_at,
        note=[
            {
                "text": (
                    event.description
                    or
                    "Condition information recorded "
                    "in the SIH Project."
                )
            }
        ],
    )


def map_medication_to_statement(
    event: TimelineEvent,
) -> FHIRMedicationStatement:

    return FHIRMedicationStatement(
        id=_resource_id(
            "MedicationStatement",
            event.event_id,
        ),
        meta=_build_meta(
            "MedicationStatement"
        ),
        status="active",
        medicationCodeableConcept=(
            _codeable_concept(
                event.title
            )
        ),
        subject=_patient_reference(
            event.patient_id
        ),
        context=(
            _encounter_reference(
                event.session_id
            )
            if event.session_id
            else None
        ),
        effectiveDateTime=event.event_date,
        dosage=[],
    )


def map_allergy_answer_to_fhir(
    answer: Answer,
    patient_id: int,
    session_id: int,
) -> FHIRAllergyIntolerance:

    return FHIRAllergyIntolerance(
        id=_resource_id(
            "AllergyIntolerance",
            answer.answer_id,
        ),
        meta=_build_meta(
            "AllergyIntolerance"
        ),
        clinicalStatus=FHIRCodeableConcept(
            text="active"
        ),
        verificationStatus=FHIRCodeableConcept(
            text="reported"
        ),
        code=_codeable_concept(
            answer.answer_text
        ),
        patient=_patient_reference(
            patient_id
        ),
        recordedDate=answer.answered_at,
        note=[
            {
                "text": (
                    "Allergy information reported "
                    "during the clinical interview."
                )
            }
        ],
    )


def map_document_to_fhir(
    document: MedicalDocument,
) -> FHIRDocumentReference:

    return FHIRDocumentReference(
        id=_resource_id(
            "DocumentReference",
            document.document_id,
        ),
        meta=_build_meta(
            "DocumentReference"
        ),
        status="current",
        subject=_patient_reference(
            document.session.patient_id
        ),
        date=(
            document.document_date
            or document.created_at
        ),
        description=(
            f"Medical document: "
            f"{document.filename}"
        ),
        content=[
            {
                "attachment": {
                    "title": document.filename,
                    "contentType": document.file_type,
                    "url": document.storage_path,
                }
            }
        ],
    )


def map_document_to_diagnostic_report(
    document: MedicalDocument,
    lab_results: list[str],
) -> FHIRDiagnosticReport:

    return FHIRDiagnosticReport(
        id=_resource_id(
            "DiagnosticReport",
            document.document_id,
        ),
        meta=_build_meta(
            "DiagnosticReport"
        ),
        status="final",
        code=FHIRCodeableConcept(
            text="Medical investigation report"
        ),
        subject=_patient_reference(
            document.session.patient_id
        ),
        encounter=_encounter_reference(
            document.session_id
        ),
        effectiveDateTime=(
            document.document_date
            or document.created_at
        ),
        result=[],
        conclusion=(
            "; ".join(lab_results)
            if lab_results
            else None
        ),
    )


def map_summary_to_composition(
    summary: ClinicalSummary,
    patient_id: int,
    session_id: int,
) -> FHIRComposition:

    return FHIRComposition(
        id=_resource_id(
            "Composition",
            summary.summary_id,
        ),
        meta=_build_meta(
            "Composition"
        ),
        status="final",
        type=FHIRCodeableConcept(
            text="Clinical Summary"
        ),
        subject=_patient_reference(
            patient_id
        ),
        encounter=_encounter_reference(
            session_id
        ),
        date=summary.generated_at,
        title="AI-Generated Clinical Summary",
        section=[
            {
                "title": "Clinical Summary",
                "text": {
                    "status": "generated",
                    "div": summary.summary_text,
                },
            }
        ],
    )


def get_session_fhir_data(
    db: Session,
    session_id: int,
) -> dict:

    clinical_session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id
            == session_id
        )
        .first()
    )

    if clinical_session is None:
        raise ValueError(
            "Session not found"
        )

    patient = (
        db.query(Patient)
        .filter(
            Patient.patient_id
            == clinical_session.patient_id
        )
        .first()
    )

    if patient is None:
        raise ValueError(
            "Patient not found"
        )

    interviews = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
        )
        .order_by(
            Interview.created_at.asc(),
            Interview.interview_id.asc(),
        )
        .all()
    )

    timeline_events = (
        db.query(TimelineEvent)
        .filter(
            TimelineEvent.patient_id
            == patient.patient_id,
            TimelineEvent.session_id
            == session_id,
        )
        .order_by(
            TimelineEvent.event_date.asc().nullslast(),
            TimelineEvent.created_at.asc(),
            TimelineEvent.event_id.asc(),
        )
        .all()
    )

    documents = (
        db.query(MedicalDocument)
        .filter(
            MedicalDocument.session_id
            == session_id
        )
        .order_by(
            MedicalDocument.document_date.asc().nullslast(),
            MedicalDocument.created_at.asc(),
            MedicalDocument.document_id.asc(),
        )
        .all()
    )

    latest_summary = (
        db.query(ClinicalSummary)
        .filter(
            ClinicalSummary.session_id
            == session_id
        )
        .order_by(
            ClinicalSummary.generated_at.desc(),
            ClinicalSummary.summary_id.desc(),
        )
        .first()
    )

    return {
        "patient": patient,
        "session": clinical_session,
        "interviews": interviews,
        "timeline_events": timeline_events,
        "documents": documents,
        "latest_summary": latest_summary,
    }


def build_session_fhir_bundle(
    db: Session,
    session_id: int,
) -> FHIRBundle:

    data = get_session_fhir_data(
        db,
        session_id,
    )

    patient = data["patient"]
    clinical_session = data["session"]
    interviews = data["interviews"]
    timeline_events = data["timeline_events"]
    documents = data["documents"]
    latest_summary = data["latest_summary"]

    resources = []

    resources.append(
        map_patient_to_fhir(
            patient
        )
    )

    resources.append(
        map_session_to_fhir(
            clinical_session
        )
    )

    for interview in interviews:

        resources.append(
            map_interview_to_fhir(
                db,
                interview,
            )
        )

    for event in timeline_events:

        if event.event_type == "diagnosis":

            resources.append(
                map_diagnosis_to_condition(
                    event
                )
            )

        elif event.event_type == "medication":

            resources.append(
                map_medication_to_statement(
                    event
                )
            )

        elif event.event_type in {
            "symptom",
            "lab_result",
            "treatment",
            "procedure",
            "consultation",
        }:

            resources.append(
                map_timeline_event_to_observation(
                    event
                )
            )

    for document in documents:

        resources.append(
            map_document_to_fhir(
                document
            )
        )

        if document.extracted_data:

            try:

                extracted_data = json.loads(
                    document.extracted_data
                )

            except (
                json.JSONDecodeError,
                TypeError,
            ):

                extracted_data = {}

            lab_results = extracted_data.get(
                "lab_results",
                [],
            )

            if lab_results:

                resources.append(
                    map_document_to_diagnostic_report(
                        document,
                        lab_results,
                    )
                )

    if latest_summary is not None:

        resources.append(
            map_summary_to_composition(
                latest_summary,
                patient.patient_id,
                clinical_session.session_id,
            )
        )

    entries = []

    for resource in resources:

        resource_data = resource.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        if resource.resourceType == "Encounter":

            encounter_class = getattr(
                resource,
                "encounter_class",
                None,
            )

            if encounter_class is not None:

                if hasattr(
                    encounter_class,
                    "model_dump",
                ):

                    encounter_class = (
                        encounter_class.model_dump(
                            by_alias=True,
                            exclude_none=True,
                        )
                    )

                resource_data["class"] = (
                    encounter_class
                )

            resource_data.pop(
                "encounter_class",
                None,
            )

        entries.append(
            FHIRBundleEntry(
                fullUrl=(
                    f"{FHIR_BASE_URL}/"
                    f"{resource.resourceType}/"
                    f"{resource.id}"
                ),
                resource=resource_data,
            )
        )

    return FHIRBundle(
        id=_resource_id(
            "Bundle",
            session_id,
        ),
        type="collection",
        timestamp=datetime.now(timezone.utc),
        entry=entries,
    )