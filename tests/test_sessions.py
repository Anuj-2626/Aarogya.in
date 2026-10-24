def create_test_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Session Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 201

    return response.json()["patient_id"]


def create_test_patient_with_language(client, language):
    response = client.post(
        "/patients/",
        json={
            "name": "Language Test Patient",
            "preferred_language": language,
        },
    )

    assert response.status_code == 201

    return response.json()["patient_id"]


def test_create_session(client):
    patient_id = create_test_patient(client)

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "session_type": "clinical_intake",
            "language": "en",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["session_id"] == 1
    assert data["patient_id"] == patient_id
    assert data["session_type"] == "clinical_intake"
    assert data["language"] == "en"
    assert data["status"] == "active"
    assert data["consent_status"] == "pending"
    assert data["completed_at"] is None
    assert "started_at" in data
    assert "created_at" in data


def test_create_session_with_default_session_type(client):
    patient_id = create_test_patient(client)

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["session_type"] == "clinical_intake"
    assert data["language"] == "en"
    assert data["status"] == "active"


def test_create_session_uses_patient_preferred_language(client):
    patient_id = create_test_patient_with_language(client, "mr")

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["language"] == "mr"


def test_create_session_explicit_language_overrides_patient_language(client):
    patient_id = create_test_patient_with_language(client, "mr")

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "language": "hi",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["language"] == "hi"


def test_create_session_with_nonexistent_patient(client):
    response = client.post(
        "/sessions/",
        json={
            "patient_id": 999999,
            "language": "en",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_create_session_with_invalid_language(client):
    patient_id = create_test_patient(client)

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "language": "xx",
        },
    )

    assert response.status_code == 422


def test_create_session_missing_patient_id(client):
    response = client.post(
        "/sessions/",
        json={
            "language": "en",
        },
    )

    assert response.status_code == 422


def test_get_sessions(client):
    patient_id = create_test_patient(client)

    client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "language": "en",
        },
    )

    response = client.get("/sessions/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["patient_id"] == patient_id
    assert data[0]["language"] == "en"


def test_get_session(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "language": "en",
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.get(f"/sessions/{session_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["patient_id"] == patient_id
    assert data["status"] == "active"


def test_get_nonexistent_session(client):
    response = client.get("/sessions/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_update_session_type(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "session_type": "follow_up",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["session_type"] == "follow_up"
    assert data["status"] == "active"


def test_update_session_language(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "language": "en",
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "language": "mr",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["language"] == "mr"


def test_complete_session(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_update_session_consent_status(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "consent_status": "granted",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["consent_status"] == "granted"


def test_update_nonexistent_session(client):
    response = client.put(
        "/sessions/999999",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_update_session_with_empty_session_type(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "session_type": "",
        },
    )

    assert response.status_code == 422


def test_update_session_with_invalid_status(client):
    patient_id = create_test_patient(client)

    create_response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
        },
    )

    session_id = create_response.json()["session_id"]

    response = client.put(
        f"/sessions/{session_id}",
        json={
            "status": "invalid_status",
        },
    )

    assert response.status_code == 422