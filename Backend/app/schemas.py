from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SUPPORTED_LANGUAGE_CODES = Literal[
    "en",
    "hi",
    "mr",
    "bn",
    "ta",
]


# ============================================================
# PATIENT SCHEMAS
# ============================================================


class PatientBase(BaseModel):
    name: str
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    preferred_language: SUPPORTED_LANGUAGE_CODES = "en"


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    preferred_language: SUPPORTED_LANGUAGE_CODES | None = None


class PatientResponse(PatientBase):
    patient_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SESSION SCHEMAS
# ============================================================


class SessionBase(BaseModel):
    session_type: str = Field(
        default="clinical_intake",
        min_length=1,
    )


class SessionCreate(SessionBase):
    patient_id: int
    language: SUPPORTED_LANGUAGE_CODES | None = None


class SessionUpdate(BaseModel):
    session_type: str | None = Field(
        default=None,
        min_length=1,
    )
    status: Literal["active", "completed"] | None = None
    language: SUPPORTED_LANGUAGE_CODES | None = None
    consent_status: str | None = None


class SessionResponse(SessionBase):
    session_id: int
    patient_id: int
    language: SUPPORTED_LANGUAGE_CODES
    status: str
    started_at: datetime
    completed_at: datetime | None
    consent_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CONSENT SCHEMAS
# ============================================================


class ConsentBase(BaseModel):
    consent_type: str = Field(
        min_length=1,
    )


class ConsentCreate(ConsentBase):
    session_id: int
    status: Literal[
        "pending",
        "granted",
        "withdrawn",
    ] = "granted"


class ConsentUpdate(BaseModel):
    status: Literal[
        "pending",
        "granted",
        "withdrawn",
    ] | None = None


class ConsentResponse(ConsentBase):
    consent_id: int
    session_id: int
    status: str
    granted_at: datetime | None
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# USER / AUTHENTICATION SCHEMAS
# ============================================================


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    role: Literal[
        "patient",
        "doctor",
        "admin",
    ] = "patient"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# INTERVIEW SCHEMAS
# ============================================================


class InterviewCreate(BaseModel):
    session_id: int
    interview_type: str = "clinical_history"
    language: SUPPORTED_LANGUAGE_CODES | None = None


class InterviewUpdate(BaseModel):
    status: Literal[
        "not_started",
        "in_progress",
        "completed",
    ] | None = None
    language: SUPPORTED_LANGUAGE_CODES | None = None


class InterviewResponse(BaseModel):
    interview_id: int
    session_id: int
    interview_type: str
    status: str
    current_question_id: int | None
    language: SUPPORTED_LANGUAGE_CODES
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# QUESTION SCHEMAS
# ============================================================


class QuestionResponse(BaseModel):
    question_id: int
    interview_id: int
    question_code: str
    question_text: str
    question_type: str
    history_section: str
    sequence_number: int
    is_required: bool
    parent_question_id: str | None
    language: SUPPORTED_LANGUAGE_CODES
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ANSWER SCHEMAS
# ============================================================


class AnswerCreate(BaseModel):
    interview_id: int
    question_id: int
    answer_text: str = Field(
        min_length=1,
    )
    answer_type: str = "text"


class AnswerResponse(BaseModel):
    answer_id: int
    interview_id: int
    question_id: int
    answer_text: str
    answer_type: str
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# MEDICAL DOCUMENT SCHEMAS
# ============================================================


class MedicalDocumentResponse(BaseModel):
    document_id: int
    session_id: int
    filename: str
    file_type: str
    storage_path: str
    ocr_text: str | None
    ocr_status: str
    extracted_data: str | None
    document_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalDocumentData(BaseModel):
    diagnoses: list[str]
    medications: list[str]
    lab_results: list[str]
    procedures: list[str]
    dates: list[str]


class MedicalDocumentDetailResponse(BaseModel):
    document_id: int
    session_id: int
    filename: str
    file_type: str
    ocr_status: str
    ocr_text: str | None
    extracted_data: MedicalDocumentData | None
    document_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# MEDICAL TIMELINE SCHEMAS
# ============================================================


class TimelineEventCreate(BaseModel):
    patient_id: int
    session_id: int | None = None
    event_date: datetime | None = None
    event_type: str = Field(
        min_length=1,
        max_length=50,
    )
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    source_type: str = Field(
        min_length=1,
        max_length=50,
    )
    source_id: int | None = None
    structured_data: str | None = None


class TimelineEventResponse(BaseModel):
    event_id: int
    patient_id: int
    session_id: int | None
    event_date: datetime | None
    event_type: str
    title: str
    description: str | None
    source_type: str
    source_id: int | None
    structured_data: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineEventListResponse(BaseModel):
    patient_id: int
    events: list[TimelineEventResponse]
    total_events: int


# ============================================================
# CLINICAL SUMMARY SCHEMAS
# ============================================================


class ClinicalSummaryCreate(BaseModel):
    session_id: int
    summary_text: str = Field(
        min_length=1,
    )
    structured_data: str | None = None
    source_version: str | None = Field(
        default=None,
        max_length=100,
    )
    status: Literal[
        "generated",
        "failed",
        "outdated",
    ] = "generated"


class ClinicalSummaryResponse(BaseModel):
    summary_id: int
    session_id: int
    summary_text: str
    structured_data: str | None
    source_version: str | None
    status: Literal[
        "generated",
        "failed",
        "outdated",
    ]
    generated_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClinicalSummaryListResponse(BaseModel):
    session_id: int
    summaries: list[ClinicalSummaryResponse]
    total_summaries: int


# ============================================================
# DOCTOR DASHBOARD SCHEMAS
# ============================================================


class DoctorDashboardRedFlag(BaseModel):
    safety_flag_id: int
    interview_id: int
    question_id: int
    category: str
    severity: str
    message: str
    detected_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class DoctorDashboardClinicalAnswer(BaseModel):
    answer_id: int
    interview_id: int
    question_id: int
    question_code: str
    question_text: str
    history_section: str
    answer_text: str
    answer_type: str
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorDashboardInterview(BaseModel):
    interview: InterviewResponse
    answers: list[DoctorDashboardClinicalAnswer]
    red_flags: list[DoctorDashboardRedFlag]


class DoctorDashboardResponse(BaseModel):
    patient: PatientResponse
    session: SessionResponse
    interviews: list[DoctorDashboardInterview]
    latest_summary: ClinicalSummaryResponse | None
    timeline: list[TimelineEventResponse]
    documents: list[MedicalDocumentDetailResponse]


# ============================================================
# CONSULTATION SCHEMAS
# ============================================================


class ConsultationCreate(BaseModel):
    session_id: int

    clinical_notes: str | None = None
    assessment: str | None = None
    diagnosis: str | None = None
    treatment_plan: str | None = None
    follow_up: str | None = None


class ConsultationUpdate(BaseModel):
    status: Literal[
        "draft",
        "completed",
    ] | None = None

    clinical_notes: str | None = None
    assessment: str | None = None
    diagnosis: str | None = None
    treatment_plan: str | None = None
    follow_up: str | None = None


class ConsultationResponse(BaseModel):
    consultation_id: int
    session_id: int
    doctor_user_id: int
    status: Literal[
        "draft",
        "completed",
    ]
    clinical_notes: str | None
    assessment: str | None
    diagnosis: str | None
    treatment_plan: str | None
    follow_up: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ConsultationListResponse(BaseModel):
    session_id: int
    consultations: list[ConsultationResponse]
    total_consultations: int


# ============================================================
# FHIR / ABDM INTEROPERABILITY SCHEMAS
# ============================================================


class FHIRMeta(BaseModel):
    profile: list[str] = []


class FHIRIdentifier(BaseModel):
    system: str | None = None
    value: str | None = None


class FHIRReference(BaseModel):
    reference: str | None = None
    display: str | None = None


class FHIRCodeableConcept(BaseModel):
    text: str | None = None
    coding: list[dict] = []


class FHIRPeriod(BaseModel):
    start: datetime | None = None
    end: datetime | None = None


class FHIRPatient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: str
    meta: FHIRMeta | None = None
    identifier: list[FHIRIdentifier] = []
    name: list[dict] = []
    birthDate: str | None = None
    gender: str | None = None
    telecom: list[dict] = []


class FHIREncounter(BaseModel):
    resourceType: Literal["Encounter"] = "Encounter"
    id: str
    meta: FHIRMeta | None = None
    identifier: list[FHIRIdentifier] = []
    status: str
    encounter_class: dict | None = Field(
        default=None,
        alias="class",
    )
    subject: FHIRReference
    period: FHIRPeriod | None = None

    model_config = ConfigDict(
        populate_by_name=True,
    )


class FHIRQuestionnaireResponseItem(BaseModel):
    linkId: str
    text: str | None = None
    answer: list[dict] = []


class FHIRQuestionnaireResponse(BaseModel):
    resourceType: Literal["QuestionnaireResponse"] = "QuestionnaireResponse"
    id: str
    meta: FHIRMeta | None = None
    status: str
    subject: FHIRReference | None = None
    encounter: FHIRReference | None = None
    authored: datetime | None = None
    item: list[FHIRQuestionnaireResponseItem] = []


class FHIRObservation(BaseModel):
    resourceType: Literal["Observation"] = "Observation"
    id: str
    meta: FHIRMeta | None = None
    status: str
    code: FHIRCodeableConcept
    subject: FHIRReference | None = None
    encounter: FHIRReference | None = None
    effectiveDateTime: datetime | None = None
    valueString: str | None = None
    note: list[dict] = []


class FHIRCondition(BaseModel):
    resourceType: Literal["Condition"] = "Condition"
    id: str
    meta: FHIRMeta | None = None
    status: FHIRCodeableConcept | None = None
    verificationStatus: FHIRCodeableConcept | None = None
    code: FHIRCodeableConcept
    subject: FHIRReference
    encounter: FHIRReference | None = None
    recordedDate: datetime | None = None
    note: list[dict] = []


class FHIRMedicationStatement(BaseModel):
    resourceType: Literal["MedicationStatement"] = "MedicationStatement"
    id: str
    meta: FHIRMeta | None = None
    status: str
    medicationCodeableConcept: FHIRCodeableConcept | None = None
    subject: FHIRReference
    context: FHIRReference | None = None
    effectiveDateTime: datetime | None = None
    dosage: list[dict] = []


class FHIRAllergyIntolerance(BaseModel):
    resourceType: Literal["AllergyIntolerance"] = "AllergyIntolerance"
    id: str
    meta: FHIRMeta | None = None
    status: FHIRCodeableConcept | None = None
    verificationStatus: FHIRCodeableConcept | None = None
    code: FHIRCodeableConcept
    patient: FHIRReference
    recordedDate: datetime | None = None
    note: list[dict] = []


class FHIRDocumentReference(BaseModel):
    resourceType: Literal["DocumentReference"] = "DocumentReference"
    id: str
    meta: FHIRMeta | None = None
    status: str
    subject: FHIRReference | None = None
    date: datetime | None = None
    description: str | None = None
    content: list[dict] = []


class FHIRDiagnosticReport(BaseModel):
    resourceType: Literal["DiagnosticReport"] = "DiagnosticReport"
    id: str
    meta: FHIRMeta | None = None
    status: str
    code: FHIRCodeableConcept
    subject: FHIRReference | None = None
    encounter: FHIRReference | None = None
    effectiveDateTime: datetime | None = None
    result: list[FHIRReference] = []
    conclusion: str | None = None


class FHIRComposition(BaseModel):
    resourceType: Literal["Composition"] = "Composition"
    id: str
    meta: FHIRMeta | None = None
    status: str
    type: FHIRCodeableConcept
    subject: FHIRReference
    encounter: FHIRReference | None = None
    date: datetime | None = None
    title: str
    section: list[dict] = []


class FHIRBundleEntry(BaseModel):
    fullUrl: str | None = None
    resource: dict


class FHIRBundle(BaseModel):
    resourceType: Literal["Bundle"] = "Bundle"
    id: str
    type: str
    timestamp: datetime | None = None
    entry: list[FHIRBundleEntry] = []