def create_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Answer Test Patient",
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


def get_questions(client, interview_id):
    response = client.get(
        f"/questions/interview/{interview_id}"
    )

    assert response.status_code == 200

    questions = response.json()
    assert len(questions) > 0

    return questions


def submit_answer(
    client,
    interview_id,
    question_id,
    answer_text="I have been feeling fine."
):
    return client.post(
        "/answers/",
        json={
            "interview_id": interview_id,
            "question_id": question_id,
            "answer_text": answer_text,
            "answer_type": "text",
        },
    )


def test_create_answer(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    question = min(
        questions,
        key=lambda item: item["sequence_number"]
    )

    response = submit_answer(
        client,
        interview["interview_id"],
        question["question_id"]
    )

    assert response.status_code == 201

    answer = response.json()

    assert answer["answer_id"] is not None
    assert answer["interview_id"] == interview["interview_id"]
    assert answer["question_id"] == question["question_id"]
    assert answer["answer_text"] == "I have been feeling fine."
    assert answer["answer_type"] == "text"
    assert answer["answered_at"] is not None


def test_create_answer_with_nonexistent_interview(client):
    response = client.post(
        "/answers/",
        json={
            "interview_id": 99999,
            "question_id": 99999,
            "answer_text": "Test answer",
            "answer_type": "text",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"


def test_create_answer_with_nonexistent_question(client):
    patient, session, interview = create_interview(client)

    response = submit_answer(
        client,
        interview["interview_id"],
        99999
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"


def test_answer_question_from_different_interview(client):
    patient_1, session_1, interview_1 = create_interview(client)

    patient_2 = create_patient(client)
    session_2 = create_session(
        client,
        patient_2["patient_id"]
    )
    grant_ai_consent(
        client,
        session_2["session_id"]
    )

    response = client.post(
        "/interviews/",
        json={
            "session_id": session_2["session_id"],
            "interview_type": "clinical_history",
            "language": "en",
        },
    )

    assert response.status_code == 201

    interview_2 = response.json()

    questions_1 = get_questions(
        client,
        interview_1["interview_id"]
    )

    question_from_interview_1 = min(
        questions_1,
        key=lambda item: item["sequence_number"]
    )

    response = submit_answer(
        client,
        interview_2["interview_id"],
        question_from_interview_1["question_id"]
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Question does not belong to this interview"
    )


def test_create_answer_requires_non_empty_text(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    question = questions[0]

    response = client.post(
        "/answers/",
        json={
            "interview_id": interview["interview_id"],
            "question_id": question["question_id"],
            "answer_text": "",
            "answer_type": "text",
        },
    )

    assert response.status_code == 422


def test_create_answer_uses_default_answer_type(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    question = questions[0]

    response = client.post(
        "/answers/",
        json={
            "interview_id": interview["interview_id"],
            "question_id": question["question_id"],
            "answer_text": "No significant symptoms.",
        },
    )

    assert response.status_code == 201

    answer = response.json()

    assert answer["answer_type"] == "text"


def test_get_interview_answers(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    question = questions[0]

    answer_response = submit_answer(
        client,
        interview["interview_id"],
        question["question_id"]
    )

    assert answer_response.status_code == 201

    response = client.get(
        f"/answers/interview/{interview['interview_id']}"
    )

    assert response.status_code == 200

    answers = response.json()

    assert len(answers) == 1
    assert answers[0]["interview_id"] == interview["interview_id"]
    assert answers[0]["question_id"] == question["question_id"]


def test_get_answers_for_nonexistent_interview(client):
    response = client.get(
        "/answers/interview/99999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"


def test_get_answer(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    question = questions[0]

    answer_response = submit_answer(
        client,
        interview["interview_id"],
        question["question_id"]
    )

    assert answer_response.status_code == 201

    answer = answer_response.json()

    response = client.get(
        f"/answers/{answer['answer_id']}"
    )

    assert response.status_code == 200
    assert response.json()["answer_id"] == answer["answer_id"]


def test_get_nonexistent_answer(client):
    response = client.get(
        "/answers/99999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Answer not found"


def test_answer_updates_current_question(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    first_question = min(
        questions,
        key=lambda item: item["sequence_number"]
    )

    response = submit_answer(
        client,
        interview["interview_id"],
        first_question["question_id"]
    )

    assert response.status_code == 201

    interview_response = client.get(
        f"/interviews/{interview['interview_id']}"
    )

    assert interview_response.status_code == 200

    updated_interview = interview_response.json()

    assert updated_interview["current_question_id"] != (
        first_question["question_id"]
    ) or updated_interview["status"] == "completed"


def test_answer_creates_timeline_event(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    question = questions[0]

    response = submit_answer(
        client,
        interview["interview_id"],
        question["question_id"]
    )

    assert response.status_code == 201

    timeline_response = client.get(
        f"/timeline/patient/{patient['patient_id']}"
    )

    assert timeline_response.status_code == 200

    timeline_data = timeline_response.json()

    assert timeline_data["total_events"] >= 1

    answer_events = [
    event
    for event in timeline_data["events"]
    if event["source_type"] == "interview"
    and event["source_id"] == response.json()["answer_id"]
]

    assert len(answer_events) >= 1
