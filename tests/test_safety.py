
from Backend.app.safety.detector import red_flag_detector
from Backend.app.safety.decisions import SafetyDecisionType


def create_interview(client):
    patient_response = client.post(
        "/patients/",
        json={
            "name": "Safety Test Patient",
            "date_of_birth": "2000-01-01",
            "gender": "male",
            "phone": "9999999999",
            "preferred_language": "en"
        }
    )

    assert patient_response.status_code == 201
    patient = patient_response.json()

    session_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient["patient_id"],
            "session_type": "clinical_intake",
            "language": "en"
        }
    )

    assert session_response.status_code == 201
    session = session_response.json()

    consent_response = client.post(
        "/consents/",
        json={
            "session_id": session["session_id"],
            "consent_type": "ai_processing",
            "status": "granted"
        }
    )

    assert consent_response.status_code == 201

    interview_response = client.post(
        "/interviews/",
        json={
            "session_id": session["session_id"],
            "interview_type": "clinical_history",
            "language": "en"
        }
    )

    assert interview_response.status_code == 201

    return patient, session, interview_response.json()


def get_questions(client, interview_id):
    response = client.get(
        f"/questions/interview/{interview_id}"
    )

    assert response.status_code == 200

    return response.json()


def submit_answer(
    client,
    interview_id,
    question_id,
    answer_text
):
    return client.post(
        "/answers/",
        json={
            "interview_id": interview_id,
            "question_id": question_id,
            "answer_text": answer_text,
            "answer_type": "text"
        }
    )


def test_detector_returns_clear_for_non_red_flag_question():
    decision = red_flag_detector.detect(
        question_code="CC_MAIN",
        answer="yes"
    )

    assert decision.decision == SafetyDecisionType.CLEAR
    assert decision.question_code == "CC_MAIN"


def test_detector_returns_clear_for_non_trigger_answer():
    decision = red_flag_detector.detect(
        question_code="RED_FLAG_CHEST",
        answer="no"
    )

    assert decision.decision == SafetyDecisionType.CLEAR
    assert decision.question_code == "RED_FLAG_CHEST"


def test_detector_flags_chest_red_flag():
    decision = red_flag_detector.detect(
        question_code="RED_FLAG_CHEST",
        answer="yes"
    )

    assert decision.decision == SafetyDecisionType.FLAG
    assert decision.question_code == "RED_FLAG_CHEST"
    assert decision.category == "chest_pain"
    assert decision.severity == "high"
    assert decision.message is not None


def test_detector_flags_breathing_red_flag():
    decision = red_flag_detector.detect(
        question_code="RED_FLAG_BREATHING",
        answer="yes"
    )

    assert decision.decision == SafetyDecisionType.FLAG
    assert decision.question_code == "RED_FLAG_BREATHING"
    assert decision.category == "breathing_difficulty"
    assert decision.severity == "high"


def test_detector_flags_consciousness_red_flag():
    decision = red_flag_detector.detect(
        question_code="RED_FLAG_CONSCIOUSNESS",
        answer="yes"
    )

    assert decision.decision == SafetyDecisionType.FLAG
    assert decision.question_code == "RED_FLAG_CONSCIOUSNESS"
    assert decision.category == "altered_consciousness"
    assert decision.severity == "high"


def test_detector_normalizes_trigger_answer():
    for answer in ["yes", "YES", " Yes ", "y", "Y", " true ", "TRUE"]:
        decision = red_flag_detector.detect(
            question_code="RED_FLAG_CHEST",
            answer=answer
        )

        assert decision.decision == SafetyDecisionType.FLAG


def test_detector_does_not_flag_similar_but_invalid_answer():
    for answer in ["yeah", "yup", "1", "true story", "yes please"]:
        decision = red_flag_detector.detect(
            question_code="RED_FLAG_CHEST",
            answer=answer
        )

        assert decision.decision == SafetyDecisionType.CLEAR


def test_safety_flags_are_created_when_answer_triggers_red_flag(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    red_flag_question = next(
        question
        for question in questions
        if question["question_code"] == "RED_FLAG_CHEST"
    )

    response = submit_answer(
        client,
        interview["interview_id"],
        red_flag_question["question_id"],
        "yes"
    )

    assert response.status_code == 201

    safety_response = client.get(
        f"/safety/interview/{interview['interview_id']}"
    )

    assert safety_response.status_code == 200

    flags = safety_response.json()

    assert len(flags) == 1

    flag = flags[0]

    assert flag["interview_id"] == interview["interview_id"]
    assert flag["question_id"] == red_flag_question["question_id"]
    assert flag["category"] == "chest_pain"
    assert flag["severity"] == "high"
    assert flag["status"] == "active"
    assert flag["message"] == (
        "Potential chest-related red flag detected. "
        "Clinician attention is required."
    )


def test_safety_flag_is_not_created_for_clear_answer(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    red_flag_question = next(
        question
        for question in questions
        if question["question_code"] == "RED_FLAG_CHEST"
    )

    response = submit_answer(
        client,
        interview["interview_id"],
        red_flag_question["question_id"],
        "no"
    )

    assert response.status_code == 201

    safety_response = client.get(
        f"/safety/interview/{interview['interview_id']}"
    )

    assert safety_response.status_code == 200
    assert safety_response.json() == []


def test_duplicate_active_safety_flag_is_not_created(client):
    patient, session, interview = create_interview(client)

    questions = get_questions(
        client,
        interview["interview_id"]
    )

    red_flag_question = next(
        question
        for question in questions
        if question["question_code"] == "RED_FLAG_CHEST"
    )

    first_response = submit_answer(
        client,
        interview["interview_id"],
        red_flag_question["question_id"],
        "yes"
    )

    assert first_response.status_code == 201

    second_response = submit_answer(
        client,
        interview["interview_id"],
        red_flag_question["question_id"],
        "YES"
    )

    assert second_response.status_code == 201

    safety_response = client.get(
        f"/safety/interview/{interview['interview_id']}"
    )

    assert safety_response.status_code == 200

    flags = safety_response.json()

    assert len(flags) == 1


def test_get_safety_flags_for_nonexistent_interview(client):
    response = client.get(
        "/safety/interview/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"
