from Backend.app.models import (
    Answer,
    Consent,
    Interview,
    Patient,
    Question,
    SafetyFlag,
    Session as SessionModel,
    TimelineEvent,
    User,
)
from Backend.app.security import hash_password


def create_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "E2E Test Patient",
            "date_of_birth": "2000-01-01",
            "gender": "male",
            "phone": "9999999999",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_session(client, patient_id):
    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "session_type": "clinical_intake",
            "language": "en",
        },
    )

    assert response.status_code == 201

    return response.json()


def grant_ai_consent(client, session_id):
    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "ai_processing",
            "status": "granted",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_interview(client, session_id):
    response = client.post(
        "/interviews/",
        json={
            "session_id": session_id,
            "interview_type": "clinical_history",
            "language": "en",
        },
    )

    assert response.status_code == 201

    return response.json()


def get_first_question(db, interview_id):
    question = (
        db.query(Question)
        .filter(
            Question.interview_id == interview_id,
        )
        .order_by(
            Question.sequence_number.asc(),
            Question.question_id.asc(),
        )
        .first()
    )

    assert question is not None

    return question


def get_red_flag_question(db, interview_id):
    red_flag_codes = [
        "RED_FLAG_CHEST",
        "RED_FLAG_BREATHING",
        "RED_FLAG_CONSCIOUSNESS",
    ]

    question = (
        db.query(Question)
        .filter(
            Question.interview_id == interview_id,
            Question.question_code.in_(red_flag_codes),
        )
        .order_by(
            Question.sequence_number.asc(),
            Question.question_id.asc(),
        )
        .first()
    )

    assert question is not None, (
        "No red-flag question was created for this interview. "
        "Expected one of: RED_FLAG_CHEST, RED_FLAG_BREATHING, "
        "RED_FLAG_CONSCIOUSNESS"
    )

    return question


def submit_answer(client, interview_id, question_id, answer_text):
    response = client.post(
        "/answers/",
        json={
            "interview_id": interview_id,
            "question_id": question_id,
            "answer_text": answer_text,
            "answer_type": "text",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_doctor(db):
    doctor = User(
        username="e2e_test_doctor",
        password_hash=hash_password("Doctor@12345"),
        role="doctor",
        is_active=True,
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


def login_doctor(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "e2e_test_doctor",
            "password": "Doctor@12345",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_complete_patient_to_session_workflow(client):
    patient_data = create_patient(client)

    patient_id = patient_data["patient_id"]

    response = client.get(
        f"/patients/{patient_id}",
    )

    assert response.status_code == 200

    fetched_patient = response.json()

    assert fetched_patient["patient_id"] == patient_id
    assert fetched_patient["name"] == "E2E Test Patient"

    session_data = create_session(
        client,
        patient_id,
    )

    assert session_data["patient_id"] == patient_id
    assert session_data["status"] == "active"
    assert session_data["language"] == "en"


def test_complete_session_to_consent_to_interview_workflow(
    client,
):
    patient_data = create_patient(client)

    session_data = create_session(
        client,
        patient_data["patient_id"],
    )

    session_id = session_data["session_id"]

    consent_data = grant_ai_consent(
        client,
        session_id,
    )

    assert consent_data["session_id"] == session_id
    assert consent_data["consent_type"] == "ai_processing"
    assert consent_data["status"] == "granted"
    assert consent_data["granted_at"] is not None

    interview_data = create_interview(
        client,
        session_id,
    )

    assert interview_data["session_id"] == session_id
    assert interview_data["status"] == "not_started"
    assert interview_data["language"] == "en"

    response = client.get(
        f"/interviews/{interview_data['interview_id']}",
    )

    assert response.status_code == 200

    fetched_interview = response.json()

    assert fetched_interview["interview_id"] == interview_data["interview_id"]
    assert fetched_interview["session_id"] == session_id


def test_complete_interview_to_answer_to_timeline_workflow(
    client,
    db,
):
    patient_data = create_patient(client)

    session_data = create_session(
        client,
        patient_data["patient_id"],
    )

    session_id = session_data["session_id"]

    grant_ai_consent(
        client,
        session_id,
    )

    interview_data = create_interview(
        client,
        session_id,
    )

    interview_id = interview_data["interview_id"]

    question = get_first_question(
        db,
        interview_id,
    )

    answer_data = submit_answer(
        client,
        interview_id,
        question.question_id,
        "I have been experiencing this symptom for two days.",
    )

    answer_id = answer_data["answer_id"]

    assert answer_data["interview_id"] == interview_id
    assert answer_data["question_id"] == question.question_id
    assert answer_data["answer_text"] == (
        "I have been experiencing this symptom for two days."
    )

    db.expire_all()

    answer = (
        db.query(Answer)
        .filter(
            Answer.answer_id == answer_id,
        )
        .first()
    )

    assert answer is not None

    timeline_event = (
        db.query(TimelineEvent)
        .filter(
            TimelineEvent.source_type == "interview",
            TimelineEvent.source_id == answer_id,
        )
        .first()
    )

    assert timeline_event is not None
    assert timeline_event.patient_id == patient_data["patient_id"]
    assert timeline_event.session_id == session_id
    assert timeline_event.event_type == "symptom"


def test_complete_answer_to_red_flag_workflow(
    client,
    db,
):
    patient_data = create_patient(client)

    session_data = create_session(
        client,
        patient_data["patient_id"],
    )

    session_id = session_data["session_id"]

    grant_ai_consent(
        client,
        session_id,
    )

    interview_data = create_interview(
        client,
        session_id,
    )

    interview_id = interview_data["interview_id"]

    question = get_red_flag_question(
        db,
        interview_id,
    )

    answer_data = submit_answer(
        client,
        interview_id,
        question.question_id,
        "yes",
    )

    answer_id = answer_data["answer_id"]

    assert answer_data["answer_id"] == answer_id
    assert answer_data["interview_id"] == interview_id
    assert answer_data["question_id"] == question.question_id
    assert answer_data["answer_text"] == "yes"

    db.expire_all()

    flags = (
        db.query(SafetyFlag)
        .filter(
            SafetyFlag.interview_id == interview_id,
            SafetyFlag.status == "active",
        )
        .all()
    )

    assert len(flags) >= 1

    flag = next(
        (
            item
            for item in flags
            if item.question_id == question.question_id
        ),
        None,
    )

    assert flag is not None
    assert flag.interview_id == interview_id
    assert flag.question_id == question.question_id
    assert flag.category is not None
    assert flag.severity == "high"
    assert flag.message is not None

    expected_categories = {
        "RED_FLAG_CHEST": "chest_pain",
        "RED_FLAG_BREATHING": "breathing_difficulty",
        "RED_FLAG_CONSCIOUSNESS": "altered_consciousness",
    }

    assert flag.category == expected_categories[question.question_code]


def test_complete_session_to_doctor_dashboard_workflow(
    client,
    db,
):
    patient_data = create_patient(client)

    session_data = create_session(
        client,
        patient_data["patient_id"],
    )

    session_id = session_data["session_id"]

    grant_ai_consent(
        client,
        session_id,
    )

    interview_data = create_interview(
        client,
        session_id,
    )

    interview_id = interview_data["interview_id"]

    question = get_first_question(
        db,
        interview_id,
    )

    submit_answer(
        client,
        interview_id,
        question.question_id,
        "Dashboard integration test answer.",
    )

    create_doctor(db)

    token = login_doctor(client)

    response = client.get(
        f"/doctor-dashboard/session/{session_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    dashboard = response.json()

    assert dashboard["patient"]["patient_id"] == patient_data["patient_id"]
    assert dashboard["session"]["session_id"] == session_id
    assert dashboard["session"]["patient_id"] == patient_data["patient_id"]

    assert len(dashboard["interviews"]) >= 1

    dashboard_interview = next(
        item
        for item in dashboard["interviews"]
        if item["interview"]["interview_id"] == interview_id
    )

    assert len(dashboard_interview["answers"]) >= 1

    dashboard_answer = next(
        item
        for item in dashboard_interview["answers"]
        if item["answer_text"] == "Dashboard integration test answer."
    )

    assert dashboard_answer["answer_text"] == (
        "Dashboard integration test answer."
    )
    assert dashboard_answer["question_id"] == question.question_id


def test_complete_session_to_fhir_workflow(
    client,
    db,
):
    patient_data = create_patient(client)

    session_data = create_session(
        client,
        patient_data["patient_id"],
    )

    session_id = session_data["session_id"]

    grant_ai_consent(
        client,
        session_id,
    )

    interview_data = create_interview(
        client,
        session_id,
    )

    interview_id = interview_data["interview_id"]

    question = get_first_question(
        db,
        interview_id,
    )

    submit_answer(
        client,
        interview_id,
        question.question_id,
        "FHIR integration test answer.",
    )

    create_doctor(db)

    token = login_doctor(client)

    response = client.get(
        f"/fhir/session/{session_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    bundle = response.json()

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"
    assert len(bundle["entry"]) >= 2

    resources = [
        entry["resource"]
        for entry in bundle["entry"]
    ]

    resource_types = {
        resource["resourceType"]
        for resource in resources
    }

    assert "Patient" in resource_types
    assert "Encounter" in resource_types

    patient_resource = next(
        resource
        for resource in resources
        if resource["resourceType"] == "Patient"
    )

    encounter_resource = next(
        resource
        for resource in resources
        if resource["resourceType"] == "Encounter"
    )

    assert patient_resource["id"] == (
        f"patient-{patient_data['patient_id']}"
    )

    # The FHIR Encounter has its own FHIR resource identifier.
    # It is intentionally not the same identifier as the internal
    # clinical session.
    assert encounter_resource["id"] == (
        f"encounter-{session_id}"
    )

    assert encounter_resource["subject"]["reference"] == (
        f"Patient/patient-{patient_data['patient_id']}"
    )

    assert encounter_resource["class"]["code"] == "OPD"


def test_full_cross_module_data_consistency(
    client,
    db,
):
    patient_data = create_patient(client)

    patient_id = patient_data["patient_id"]

    session_data = create_session(
        client,
        patient_id,
    )

    session_id = session_data["session_id"]

    consent_data = grant_ai_consent(
        client,
        session_id,
    )

    interview_data = create_interview(
        client,
        session_id,
    )

    interview_id = interview_data["interview_id"]

    question = get_first_question(
        db,
        interview_id,
    )

    answer_data = submit_answer(
        client,
        interview_id,
        question.question_id,
        "Full cross-module consistency test answer.",
    )

    answer_id = answer_data["answer_id"]

    db.expire_all()

    db_patient = (
        db.query(Patient)
        .filter(
            Patient.patient_id == patient_id,
        )
        .first()
    )

    db_session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id,
        )
        .first()
    )

    db_consent = (
        db.query(Consent)
        .filter(
            Consent.consent_id == consent_data["consent_id"],
        )
        .first()
    )

    db_interview = (
        db.query(Interview)
        .filter(
            Interview.interview_id == interview_id,
        )
        .first()
    )

    db_answer = (
        db.query(Answer)
        .filter(
            Answer.answer_id == answer_id,
        )
        .first()
    )

    assert db_patient is not None
    assert db_session is not None
    assert db_consent is not None
    assert db_interview is not None
    assert db_answer is not None

    assert db_session.patient_id == patient_id
    assert db_consent.session_id == session_id
    assert db_interview.session_id == session_id
    assert db_answer.interview_id == interview_id
    assert db_answer.question_id == question.question_id

    timeline_event = (
        db.query(TimelineEvent)
        .filter(
            TimelineEvent.source_type == "interview",
            TimelineEvent.source_id == answer_id,
        )
        .first()
    )

    assert timeline_event is not None
    assert timeline_event.patient_id == patient_id
    assert timeline_event.session_id == session_id

    create_doctor(db)

    token = login_doctor(client)

    dashboard_response = client.get(
        f"/doctor-dashboard/session/{session_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard_response.status_code == 200

    dashboard = dashboard_response.json()

    assert dashboard["patient"]["patient_id"] == patient_id
    assert dashboard["session"]["session_id"] == session_id

    fhir_response = client.get(
        f"/fhir/session/{session_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert fhir_response.status_code == 200

    fhir_bundle = fhir_response.json()

    assert fhir_bundle["resourceType"] == "Bundle"

    fhir_patient = next(
        entry["resource"]
        for entry in fhir_bundle["entry"]
        if entry["resource"]["resourceType"] == "Patient"
    )

    fhir_encounter = next(
        entry["resource"]
        for entry in fhir_bundle["entry"]
        if entry["resource"]["resourceType"] == "Encounter"
    )

    assert fhir_patient["id"] == f"patient-{patient_id}"

    assert fhir_encounter["id"] == (
        f"encounter-{session_id}"
    )

    assert fhir_encounter["subject"]["reference"] == (
        f"Patient/patient-{patient_id}"
    )

    assert fhir_encounter["class"]["code"] == "OPD"