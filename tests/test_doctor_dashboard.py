from datetime import datetime

from Backend.app.models import (
    Answer,
    ClinicalSummary,
    Interview,
    MedicalDocument,
    Patient,
    Question,
    SafetyFlag,
    Session as SessionModel,
    TimelineEvent,
    User,
)
from Backend.app.security import hash_password


def create_user(db_session, username, role):
    user = User(
        username=username,
        password_hash=hash_password("Test@12345"),
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_patient(db_session):
    patient = Patient(
        name="Dashboard Test Patient",
        gender="Male",
        phone="9999999999",
        preferred_language="en",
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


def create_session(db_session, patient_id):
    session = SessionModel(
        patient_id=patient_id,
        session_type="clinical_intake",
        language="en",
        status="active",
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def login(client, username):
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": "Test@12345",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_doctor_can_access_dashboard(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    token = login(
        client,
        "dashboard_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "patient" in data
    assert "session" in data
    assert "interviews" in data
    assert "latest_summary" in data
    assert "timeline" in data
    assert "documents" in data


def test_admin_can_access_dashboard(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_admin",
        "admin",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    token = login(
        client,
        "dashboard_admin",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200


def test_patient_cannot_access_dashboard(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_patient",
        "patient",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    token = login(
        client,
        "dashboard_patient",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_unauthenticated_user_cannot_access_dashboard(
    client,
    db_session,
):
    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}"
    )

    assert response.status_code == 401


def test_dashboard_returns_404_for_nonexistent_session(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_doctor_404",
        "doctor",
    )

    token = login(
        client,
        "dashboard_doctor_404",
    )

    response = client.get(
        "/doctor-dashboard/session/999999",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_dashboard_returns_patient_and_session_data(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_data_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    token = login(
        client,
        "dashboard_data_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient"]["patient_id"] == patient.patient_id
    assert data["patient"]["name"] == "Dashboard Test Patient"
    assert data["patient"]["gender"] == "Male"

    assert data["session"]["session_id"] == session.session_id
    assert data["session"]["patient_id"] == patient.patient_id
    assert data["session"]["language"] == "en"
    assert data["session"]["status"] == "active"


def test_dashboard_returns_interview_answers_and_red_flags(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_interview_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    interview = Interview(
        session_id=session.session_id,
        interview_type="clinical_history",
        status="in_progress",
        language="en",
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)

    question = Question(
        interview_id=interview.interview_id,
        question_code="CC_MAIN",
        question_text="What is your main complaint?",
        question_type="text",
        history_section="Chief Complaint",
        sequence_number=1,
        is_required=True,
        parent_question_id=None,
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    answer = Answer(
        interview_id=interview.interview_id,
        question_id=question.question_id,
        answer_text="Severe chest pain",
        answer_type="text",
    )
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)

    safety_flag = SafetyFlag(
        interview_id=interview.interview_id,
        question_id=question.question_id,
        category="chest",
        severity="high",
        message="Possible chest pain red flag",
        status="active",
    )
    db_session.add(safety_flag)
    db_session.commit()
    db_session.refresh(safety_flag)

    token = login(
        client,
        "dashboard_interview_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["interviews"]) == 1

    dashboard_interview = data["interviews"][0]

    assert (
        dashboard_interview["interview"]["interview_id"]
        == interview.interview_id
    )

    assert len(dashboard_interview["answers"]) == 1

    dashboard_answer = dashboard_interview["answers"][0]

    assert dashboard_answer["answer_id"] == answer.answer_id
    assert dashboard_answer["question_code"] == "CC_MAIN"
    assert dashboard_answer["answer_text"] == "Severe chest pain"

    assert len(dashboard_interview["red_flags"]) == 1

    dashboard_flag = dashboard_interview["red_flags"][0]

    assert (
        dashboard_flag["safety_flag_id"]
        == safety_flag.safety_flag_id
    )
    assert dashboard_flag["severity"] == "high"
    assert dashboard_flag["status"] == "active"


def test_dashboard_excludes_inactive_red_flags(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_flag_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    interview = Interview(
        session_id=session.session_id,
        interview_type="clinical_history",
        status="in_progress",
        language="en",
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)

    question = Question(
        interview_id=interview.interview_id,
        question_code="CC_MAIN",
        question_text="What is your main complaint?",
        question_type="text",
        history_section="Chief Complaint",
        sequence_number=1,
        is_required=True,
        parent_question_id=None,
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    active_flag = SafetyFlag(
        interview_id=interview.interview_id,
        question_id=question.question_id,
        category="chest",
        severity="high",
        message="Active red flag",
        status="active",
    )

    inactive_flag = SafetyFlag(
        interview_id=interview.interview_id,
        question_id=question.question_id,
        category="breathing",
        severity="high",
        message="Inactive red flag",
        status="resolved",
    )

    db_session.add_all([
        active_flag,
        inactive_flag,
    ])
    db_session.commit()

    token = login(
        client,
        "dashboard_flag_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    red_flags = data["interviews"][0]["red_flags"]

    assert len(red_flags) == 1
    assert red_flags[0]["message"] == "Active red flag"


def test_dashboard_returns_latest_summary(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_summary_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    older_summary = ClinicalSummary(
        session_id=session.session_id,
        summary_text="Older clinical summary",
        structured_data=None,
        source_version="timeline-v1",
        status="generated",
    )

    db_session.add(older_summary)
    db_session.commit()
    db_session.refresh(older_summary)

    newer_summary = ClinicalSummary(
        session_id=session.session_id,
        summary_text="Latest clinical summary",
        structured_data=None,
        source_version="timeline-v1",
        status="generated",
    )

    db_session.add(newer_summary)
    db_session.commit()
    db_session.refresh(newer_summary)

    token = login(
        client,
        "dashboard_summary_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["latest_summary"] is not None
    assert (
        data["latest_summary"]["summary_id"]
        == newer_summary.summary_id
    )
    assert (
        data["latest_summary"]["summary_text"]
        == "Latest clinical summary"
    )


def test_dashboard_returns_timeline_events(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_timeline_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    event = TimelineEvent(
        patient_id=patient.patient_id,
        session_id=session.session_id,
        event_date=datetime.utcnow(),
        event_type="symptom",
        title="Chest Pain",
        description="Patient reported chest pain",
        source_type="interview",
        source_id=1,
        structured_data='{"severity":"high"}',
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    token = login(
        client,
        "dashboard_timeline_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["timeline"]) == 1

    timeline_event = data["timeline"][0]

    assert timeline_event["event_id"] == event.event_id
    assert timeline_event["event_type"] == "symptom"
    assert timeline_event["title"] == "Chest Pain"
    assert (
        timeline_event["source_type"]
        == "interview"
    )


def test_dashboard_returns_documents(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_documents_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    document = MedicalDocument(
        session_id=session.session_id,
        filename="blood_report.pdf",
        file_type="application/pdf",
        storage_path="uploads/test/blood_report.pdf",
        ocr_text="Hemoglobin: 13.5 g/dL",
        ocr_status="completed",
        extracted_data=(
            '{"diagnoses":[],"medications":[],'
            '"lab_results":["Hemoglobin 13.5 g/dL"],'
            '"procedures":[],"dates":[]}'
        ),
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    token = login(
        client,
        "dashboard_documents_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["documents"]) == 1

    dashboard_document = data["documents"][0]

    assert (
        dashboard_document["document_id"]
        == document.document_id
    )
    assert (
        dashboard_document["filename"]
        == "blood_report.pdf"
    )
    assert (
        dashboard_document["ocr_status"]
        == "completed"
    )

    assert dashboard_document["extracted_data"] == {
        "diagnoses": [],
        "medications": [],
        "lab_results": ["Hemoglobin 13.5 g/dL"],
        "procedures": [],
        "dates": [],
    }


def test_dashboard_returns_empty_optional_sections(
    client,
    db_session,
):
    create_user(
        db_session,
        "dashboard_empty_doctor",
        "doctor",
    )

    patient = create_patient(db_session)
    session = create_session(
        db_session,
        patient.patient_id,
    )

    token = login(
        client,
        "dashboard_empty_doctor",
    )

    response = client.get(
        f"/doctor-dashboard/session/{session.session_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["interviews"] == []
    assert data["timeline"] == []
    assert data["documents"] == []
    assert data["latest_summary"] is None