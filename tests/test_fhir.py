from datetime import datetime

from Backend.app.models import (
    Answer,
    ClinicalSummary,
    Interview,
    MedicalDocument,
    Patient,
    Question,
    Session as SessionModel,
    TimelineEvent,
    User,
)
from Backend.app.security import create_access_token, hash_password


def create_test_user(db, username: str, role: str) -> User:
    user = User(
        username=username,
        password_hash=hash_password("TestPassword@123"),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_test_patient(db) -> Patient:
    patient = Patient(
        name="FHIR Test Patient",
        date_of_birth=datetime(2000, 1, 15),
        gender="male",
        phone="9999999999",
        preferred_language="en",
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def create_test_session(db, patient_id: int) -> SessionModel:
    session = SessionModel(
        patient_id=patient_id,
        session_type="clinical_intake",
        language="en",
        status="active",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_auth_headers(user: User) -> dict:
    token = create_access_token(
        user_id=user.user_id,
        role=user.role,
    )

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# AUTHENTICATION & ACCESS CONTROL
# ============================================================


def test_fhir_requires_authentication(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    response = client.get(
        f"/fhir/session/{session.session_id}"
    )

    assert response.status_code == 401


def test_fhir_denies_patient_role(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    patient_user = create_test_user(
        db,
        username="fhir_patient_user",
        role="patient",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(patient_user),
    )

    assert response.status_code == 403


def test_fhir_allows_doctor_role(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_doctor_user",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200


def test_fhir_allows_admin_role(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    admin = create_test_user(
        db,
        username="fhir_admin_user",
        role="admin",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(admin),
    )

    assert response.status_code == 200


# ============================================================
# INVALID RESOURCE ACCESS
# ============================================================


def test_fhir_returns_404_for_nonexistent_session(client, db):
    doctor = create_test_user(
        db,
        username="fhir_missing_session_doctor",
        role="doctor",
    )

    response = client.get(
        "/fhir/session/999999",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


# ============================================================
# FHIR BUNDLE STRUCTURE
# ============================================================


def test_fhir_bundle_has_correct_bundle_structure(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_bundle_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resourceType"] == "Bundle"
    assert data["id"] == f"bundle-{session.session_id}"
    assert data["type"] == "collection"
    assert "timestamp" in data
    assert "entry" in data

    assert isinstance(data["entry"], list)
    assert len(data["entry"]) >= 2


def test_fhir_bundle_contains_patient_resource(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_patient_resource_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    patient_entries = [
        entry
        for entry in entries
        if entry["resource"]["resourceType"] == "Patient"
    ]

    assert len(patient_entries) == 1

    fhir_patient = patient_entries[0]["resource"]

    assert fhir_patient["id"] == f"patient-{patient.patient_id}"

    assert fhir_patient["identifier"][0]["value"] == str(
        patient.patient_id
    )

    assert fhir_patient["name"][0]["text"] == patient.name
    assert fhir_patient["gender"] == patient.gender
    assert fhir_patient["birthDate"] == "2000-01-15"


def test_fhir_bundle_contains_encounter_resource(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_encounter_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    encounter_entries = [
        entry
        for entry in entries
        if entry["resource"]["resourceType"] == "Encounter"
    ]

    assert len(encounter_entries) == 1

    encounter = encounter_entries[0]["resource"]

    assert encounter["id"] == f"encounter-{session.session_id}"
    assert encounter["status"] == session.status

    assert encounter["class"]["code"] == "OPD"
    assert encounter["class"]["display"] == "Outpatient Department"

    assert (
        encounter["subject"]["reference"]
        == f"Patient/patient-{patient.patient_id}"
    )


def test_fhir_patient_reference_is_correct(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_reference_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    encounter = next(
        entry["resource"]
        for entry in entries
        if entry["resource"]["resourceType"] == "Encounter"
    )

    assert encounter["subject"]["reference"] == (
        f"Patient/patient-{patient.patient_id}"
    )


# ============================================================
# FHIR FULL RESOURCE GENERATION
# ============================================================


def test_fhir_bundle_contains_interview_questionnaire_response(
    client,
    db,
):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    interview = Interview(
        session_id=session.session_id,
        interview_type="clinical_history",
        status="completed",
        language="en",
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    question = Question(
        interview_id=interview.interview_id,
        question_code="CC_MAIN",
        question_text="What is your main complaint?",
        question_type="text",
        history_section="chief_complaint",
        sequence_number=1,
        is_required=True,
        parent_question_id=None,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    answer = Answer(
        interview_id=interview.interview_id,
        question_id=question.question_id,
        answer_text="Headache for three days",
        answer_type="text",
    )

    db.add(answer)
    db.commit()

    doctor = create_test_user(
        db,
        username="fhir_interview_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    questionnaire_entries = [
        entry
        for entry in entries
        if entry["resource"]["resourceType"]
        == "QuestionnaireResponse"
    ]

    assert len(questionnaire_entries) == 1

    questionnaire = questionnaire_entries[0]["resource"]

    assert questionnaire["id"] == (
        f"questionnaireresponse-{interview.interview_id}"
    )

    assert questionnaire["status"] == "completed"

    assert (
        questionnaire["subject"]["reference"]
        == f"Patient/patient-{patient.patient_id}"
    )

    assert (
        questionnaire["encounter"]["reference"]
        == f"Encounter/encounter-{session.session_id}"
    )

    assert len(questionnaire["item"]) == 1

    item = questionnaire["item"][0]

    assert item["linkId"] == "CC_MAIN"
    assert item["text"] == "What is your main complaint?"

    assert item["answer"][0]["valueString"] == (
        "Headache for three days"
    )


# ============================================================
# TIMELINE → FHIR RESOURCE
# ============================================================


def test_fhir_bundle_contains_timeline_observation(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    event = TimelineEvent(
        patient_id=patient.patient_id,
        session_id=session.session_id,
        event_type="symptom",
        title="Headache",
        description="Patient reports headache for three days.",
        event_date=datetime(2026, 9, 13),
        source_type="system",
        source_id=None,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    doctor = create_test_user(
        db,
        username="fhir_timeline_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    observation_entries = [
        entry
        for entry in entries
        if entry["resource"]["resourceType"]
        == "Observation"
    ]

    assert len(observation_entries) == 1

    observation = observation_entries[0]["resource"]

    assert observation["id"] == (
        f"observation-{event.event_id}"
    )

    assert observation["status"] == "final"

    assert observation["code"]["text"] == "Headache"

    assert (
        observation["subject"]["reference"]
        == f"Patient/patient-{patient.patient_id}"
    )

    assert observation["valueString"] == (
        "Patient reports headache for three days."
    )


# ============================================================
# TIMELINE → CONDITION
# ============================================================


def test_fhir_bundle_maps_diagnosis_to_condition(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    event = TimelineEvent(
        patient_id=patient.patient_id,
        session_id=session.session_id,
        event_type="diagnosis",
        title="Hypertension",
        description="Previously diagnosed hypertension.",
        event_date=datetime(2026, 9, 13),
        source_type="system",
        source_id=None,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    doctor = create_test_user(
        db,
        username="fhir_condition_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    condition_entries = [
        entry
        for entry in entries
        if entry["resource"]["resourceType"]
        == "Condition"
    ]

    assert len(condition_entries) == 1

    condition = condition_entries[0]["resource"]

    assert condition["id"] == (
        f"condition-{event.event_id}"
    )

    assert condition["clinicalStatus"]["text"] == "active"
    assert condition["verificationStatus"]["text"] == "reported"

    assert condition["code"]["text"] == "Hypertension"

    assert (
        condition["subject"]["reference"]
        == f"Patient/patient-{patient.patient_id}"
    )


# ============================================================
# TIMELINE → MEDICATION STATEMENT
# ============================================================


def test_fhir_bundle_maps_medication_to_medication_statement(
    client,
    db,
):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    event = TimelineEvent(
        patient_id=patient.patient_id,
        session_id=session.session_id,
        event_type="medication",
        title="Paracetamol",
        description="Current medication.",
        event_date=datetime(2026, 9, 13),
        source_type="system",
        source_id=None,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    doctor = create_test_user(
        db,
        username="fhir_medication_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    medication_entries = [
        entry
        for entry in entries
        if entry["resource"]["resourceType"]
        == "MedicationStatement"
    ]

    assert len(medication_entries) == 1

    medication = medication_entries[0]["resource"]

    assert medication["id"] == (
        f"medicationstatement-{event.event_id}"
    )

    assert medication["status"] == "active"

    assert (
        medication["medicationCodeableConcept"]["text"]
        == "Paracetamol"
    )

    assert (
        medication["subject"]["reference"]
        == f"Patient/patient-{patient.patient_id}"
    )


# ============================================================
# FHIR FULL URL VALIDATION
# ============================================================


def test_fhir_bundle_entries_have_full_urls(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_full_url_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    assert len(entries) >= 2

    for entry in entries:
        assert "fullUrl" in entry
        assert entry["fullUrl"].startswith(
            "urn:sih-project/"
        )

        assert "resource" in entry
        assert "resourceType" in entry["resource"]
        assert "id" in entry["resource"]


# ============================================================
# FHIR META / PROFILE VALIDATION
# ============================================================


def test_fhir_resources_contain_meta_profiles(client, db):
    patient = create_test_patient(db)
    session = create_test_session(db, patient.patient_id)

    doctor = create_test_user(
        db,
        username="fhir_meta_doctor",
        role="doctor",
    )

    response = client.get(
        f"/fhir/session/{session.session_id}",
        headers=get_auth_headers(doctor),
    )

    assert response.status_code == 200

    entries = response.json()["entry"]

    assert len(entries) >= 2

    for entry in entries:
        resource = entry["resource"]

        assert "meta" in resource
        assert "profile" in resource["meta"]
        assert len(resource["meta"]["profile"]) >= 1

        profile = resource["meta"]["profile"][0]

        assert profile.startswith(
            "urn:sih-project/StructureDefinition/"
        )