from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    preferred_language = Column(String, default="en", nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sessions = relationship(
        "Session",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    timeline_events = relationship(
        "TimelineEvent",
        back_populates="patient",
        cascade="all, delete-orphan",
    )


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),
        nullable=False,
    )

    session_type = Column(
        String,
        default="clinical_intake",
        nullable=False,
    )

    status = Column(
        String,
        default="active",
        nullable=False,
    )

    language = Column(
        String,
        default="en",
        nullable=False,
    )

    started_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    ended_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    patient = relationship(
        "Patient",
        back_populates="sessions",
    )

    interviews = relationship(
        "Interview",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    consents = relationship(
        "Consent",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    medical_documents = relationship(
        "MedicalDocument",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    timeline_events = relationship(
        "TimelineEvent",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    clinical_summaries = relationship(
        "ClinicalSummary",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    consultations = relationship(
        "Consultation",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    @property
    def completed_at(self):
        return self.ended_at

    @property
    def consent_status(self):
        if not self.consents:
            return "pending"

        if any(
            consent.status == "granted"
            for consent in self.consents
        ):
            return "granted"

        if all(
            consent.status == "withdrawn"
            for consent in self.consents
        ):
            return "revoked"

        return "pending"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        default="patient",
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    consultations = relationship(
        "Consultation",
        back_populates="doctor",
    )


class Consent(Base):
    __tablename__ = "consents"

    consent_id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=False,
    )

    consent_type = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default="granted",
        nullable=False,
    )

    granted_at = Column(
        DateTime,
        default=None,
        nullable=True,
    )

    revoked_at = Column(
        DateTime,
        nullable=True,
    )

    session = relationship(
        "Session",
        back_populates="consents",
    )


class Interview(Base):
    __tablename__ = "interviews"

    interview_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=False,
    )

    interview_type = Column(
        String,
        default="clinical_history",
        nullable=False,
    )

    status = Column(
        String,
        default="not_started",
        nullable=False,
    )

    current_question_id = Column(
        Integer,
        nullable=True,
    )

    language = Column(
        String,
        default="en",
        nullable=False,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session = relationship(
        "Session",
        back_populates="interviews",
    )

    questions = relationship(
        "Question",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

    answers = relationship(
        "Answer",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

    safety_flags = relationship(
        "SafetyFlag",
        back_populates="interview",
        cascade="all, delete-orphan",
    )


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.interview_id"),
        nullable=False,
    )

    question_code = Column(
        String,
        nullable=False,
    )

    question_text = Column(
        Text,
        nullable=False,
    )

    question_type = Column(
        String,
        nullable=False,
    )

    history_section = Column(
        String,
        nullable=False,
    )

    sequence_number = Column(
        Integer,
        nullable=False,
    )

    is_required = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    parent_question_id = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    interview = relationship(
        "Interview",
        back_populates="questions",
    )

    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    safety_flags = relationship(
        "SafetyFlag",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class Answer(Base):
    __tablename__ = "answers"

    answer_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.interview_id"),
        nullable=False,
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.question_id"),
        nullable=False,
    )

    answer_text = Column(
        Text,
        nullable=False,
    )

    answer_type = Column(
        String,
        default="text",
        nullable=False,
    )

    answered_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    interview = relationship(
        "Interview",
        back_populates="answers",
    )

    question = relationship(
        "Question",
        back_populates="answers",
    )


class SafetyFlag(Base):
    __tablename__ = "safety_flags"

    safety_flag_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.interview_id"),
        nullable=False,
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.question_id"),
        nullable=False,
    )

    category = Column(
        String,
        nullable=False,
    )

    severity = Column(
        String,
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    detected_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    status = Column(
        String,
        default="active",
        nullable=False,
    )

    interview = relationship(
        "Interview",
        back_populates="safety_flags",
    )

    question = relationship(
        "Question",
        back_populates="safety_flags",
    )


class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    document_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=False,
    )

    filename = Column(
        String,
        nullable=False,
    )

    file_type = Column(
        String,
        nullable=False,
    )

    storage_path = Column(
        String,
        nullable=False,
    )

    ocr_text = Column(
        Text,
        nullable=True,
    )

    ocr_status = Column(
        String,
        default="pending",
        nullable=False,
    )

    extracted_data = Column(
        Text,
        nullable=True,
    )

    document_date = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session = relationship(
        "Session",
        back_populates="medical_documents",
    )


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    event_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),
        nullable=False,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=True,
        index=True,
    )

    event_date = Column(
        DateTime,
        nullable=True,
        index=True,
    )

    event_type = Column(
        String,
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    source_type = Column(
        String,
        nullable=False,
    )

    source_id = Column(
        Integer,
        nullable=True,
    )

    structured_data = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    patient = relationship(
        "Patient",
        back_populates="timeline_events",
    )

    session = relationship(
        "Session",
        back_populates="timeline_events",
    )


class ClinicalSummary(Base):
    __tablename__ = "clinical_summaries"

    summary_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=False,
        index=True,
    )

    summary_text = Column(
        Text,
        nullable=False,
    )

    structured_data = Column(
        Text,
        nullable=True,
    )

    source_version = Column(
        String(100),
        nullable=True,
    )

    status = Column(
        String(20),
        nullable=False,
        default="generated",
    )

    generated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session = relationship(
        "Session",
        back_populates="clinical_summaries",
    )


class Consultation(Base):
    __tablename__ = "consultations"

    consultation_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=False,
        index=True,
    )

    doctor_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )

    status = Column(
        String,
        default="draft",
        nullable=False,
    )

    clinical_notes = Column(
        Text,
        nullable=True,
    )

    assessment = Column(
        Text,
        nullable=True,
    )

    diagnosis = Column(
        Text,
        nullable=True,
    )

    treatment_plan = Column(
        Text,
        nullable=True,
    )

    follow_up = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    session = relationship(
        "Session",
        back_populates="consultations",
    )

    doctor = relationship(
        "User",
        back_populates="consultations",
    )