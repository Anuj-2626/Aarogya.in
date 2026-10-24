def create_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Interview Test Patient",
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


def create_interview(client):
    patient = create_patient(client)
    session = create_session(client, patient["patient_id"])
    grant_ai_consent(client, session["session_id"])

    response = client.post(
        "/interviews/",
        json={
            "session_id": session["session_id"],
            "interview_type": "clinical_history",
            "language": "en",
        },
    )

    assert response.status_code == 201

    return patient, session, response.json()


def test_create_interview(client):
    patient, session, interview = create_interview(client)

    assert interview["session_id"] == session["session_id"]
    assert interview["interview_type"] == "clinical_history"
    assert interview["language"] == "en"
    assert interview["status"] == "not_started"
    assert interview["current_question_id"] is not None


def test_create_interview_requires_consent(client):
    patient = create_patient(client)
    session = create_session(client, patient["patient_id"])

    response = client.post(
        "/interviews/",
        json={
            "session_id": session["session_id"],
            "interview_type": "clinical_history",
            "language": "en",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Required consent has not been granted"
    )


def test_create_interview_with_nonexistent_session(client):
    response = client.post(
        "/interviews/",
        json={
            "session_id": 99999,
            "interview_type": "clinical_history",
            "language": "en",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_create_duplicate_interview(client):
    patient, session, interview = create_interview(client)

    response = client.post(
        "/interviews/",
        json={
            "session_id": session["session_id"],
            "interview_type": "clinical_history",
            "language": "en",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An interview already exists for this session"
    )


def test_get_interviews(client):
    patient, session, interview = create_interview(client)

    response = client.get("/interviews/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["interview_id"] == interview["interview_id"]


def test_get_interview(client):
    patient, session, interview = create_interview(client)

    response = client.get(
        f"/interviews/{interview['interview_id']}"
    )

    assert response.status_code == 200
    assert response.json()["interview_id"] == interview["interview_id"]


def test_get_nonexistent_interview(client):
    response = client.get("/interviews/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"


def test_update_interview_to_in_progress(client):
    patient, session, interview = create_interview(client)

    response = client.put(
        f"/interviews/{interview['interview_id']}",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    updated_interview = response.json()

    assert updated_interview["status"] == "in_progress"
    assert updated_interview["started_at"] is not None


def test_update_interview_to_completed(client):
    patient, session, interview = create_interview(client)

    response = client.put(
        f"/interviews/{interview['interview_id']}",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    updated_interview = response.json()

    assert updated_interview["status"] == "completed"
    assert updated_interview["completed_at"] is not None


def test_update_nonexistent_interview(client):
    response = client.put(
        "/interviews/99999",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"


def test_interview_creates_questions(client):
    patient, session, interview = create_interview(client)

    response = client.get(
        f"/questions/interview/{interview['interview_id']}"
    )

    assert response.status_code == 200

    questions = response.json()

    assert len(questions) > 0

    for question in questions:
        assert question["interview_id"] == interview["interview_id"]
        assert question["question_code"]
        assert question["question_text"]
        assert question["sequence_number"] is not None


def test_first_question_is_current_question(client):
    patient, session, interview = create_interview(client)

    response = client.get(
        f"/questions/interview/{interview['interview_id']}"
    )

    assert response.status_code == 200

    questions = response.json()

    first_question = min(
        questions,
        key=lambda question: question["sequence_number"]
    )

    assert (
        interview["current_question_id"]
        == first_question["question_id"]
    )
