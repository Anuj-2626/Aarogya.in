def create_test_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Consent Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 201

    return response.json()["patient_id"]


def create_test_session(client):
    patient_id = create_test_patient(client)

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "session_type": "clinical_intake",
        },
    )

    assert response.status_code == 201

    return response.json()["session_id"]


def create_test_consent(client, session_id, status="granted"):
    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "clinical_workflow",
            "status": status,
        },
    )

    assert response.status_code == 201

    return response.json()["consent_id"]


def test_create_consent(client):
    session_id = create_test_session(client)

    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "clinical_workflow",
            "status": "granted",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["session_id"] == session_id
    assert data["consent_type"] == "clinical_workflow"
    assert data["status"] == "granted"
    assert data["granted_at"] is not None
    assert data["revoked_at"] is None


def test_create_consent_default_status(client):
    session_id = create_test_session(client)

    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "clinical_workflow",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "granted"


def test_create_pending_consent(client):
    session_id = create_test_session(client)

    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "clinical_workflow",
            "status": "pending",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "pending"
    assert data["granted_at"] is None
    assert data["revoked_at"] is None


def test_create_withdrawn_consent(client):
    session_id = create_test_session(client)

    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "clinical_workflow",
            "status": "withdrawn",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "withdrawn"
    assert data["revoked_at"] is not None


def test_create_consent_for_nonexistent_session(client):
    response = client.post(
        "/consents/",
        json={
            "session_id": 999999,
            "consent_type": "clinical_workflow",
            "status": "granted",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_create_consent_missing_type(client):
    session_id = create_test_session(client)

    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "status": "granted",
        },
    )

    assert response.status_code == 422


def test_create_consent_invalid_status(client):
    session_id = create_test_session(client)

    response = client.post(
        "/consents/",
        json={
            "session_id": session_id,
            "consent_type": "clinical_workflow",
            "status": "invalid",
        },
    )

    assert response.status_code == 422


def test_get_consents(client):
    session_id = create_test_session(client)

    create_test_consent(client, session_id)

    response = client.get("/consents/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["session_id"] == session_id


def test_get_consent(client):
    session_id = create_test_session(client)

    consent_id = create_test_consent(
        client,
        session_id,
    )

    response = client.get(
        f"/consents/{consent_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["consent_id"] == consent_id
    assert data["session_id"] == session_id


def test_get_nonexistent_consent(client):
    response = client.get("/consents/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Consent not found"


def test_update_consent_to_withdrawn(client):
    session_id = create_test_session(client)

    consent_id = create_test_consent(
        client,
        session_id,
    )

    response = client.put(
        f"/consents/{consent_id}",
        json={
            "status": "withdrawn",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "withdrawn"
    assert data["revoked_at"] is not None


def test_update_consent_to_granted(client):
    session_id = create_test_session(client)

    consent_id = create_test_consent(
        client,
        session_id,
        status="withdrawn",
    )

    response = client.put(
        f"/consents/{consent_id}",
        json={
            "status": "granted",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "granted"
    assert data["granted_at"] is not None
    assert data["revoked_at"] is None


def test_update_consent_to_pending(client):
    session_id = create_test_session(client)

    consent_id = create_test_consent(
        client,
        session_id,
    )

    response = client.put(
        f"/consents/{consent_id}",
        json={
            "status": "pending",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "pending"
    assert data["granted_at"] is None
    assert data["revoked_at"] is None


def test_update_nonexistent_consent(client):
    response = client.put(
        "/consents/999999",
        json={
            "status": "withdrawn",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Consent not found"


def test_consent_status_reflected_by_session(client):
    session_id = create_test_session(client)

    consent_id = create_test_consent(
        client,
        session_id,
        status="granted",
    )

    response = client.get(
        f"/sessions/{session_id}"
    )

    assert response.status_code == 200
    assert response.json()["consent_status"] == "granted"

    response = client.put(
        f"/consents/{consent_id}",
        json={
            "status": "withdrawn",
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/sessions/{session_id}"
    )

    assert response.status_code == 200
    assert response.json()["consent_status"] == "revoked"