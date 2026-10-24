

def test_create_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["patient_id"] == 1
    assert data["name"] == "Test Patient"
    assert data["date_of_birth"] == "2002-05-15"
    assert data["gender"] == "Male"
    assert data["phone"] == "9876543210"
    assert data["preferred_language"] == "en"

    assert "created_at" in data
    assert "updated_at" in data


def test_get_patients(client):
    client.post(
        "/patients/",
        json={
            "name": "Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    response = client.get("/patients/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Patient"


def test_get_patient(client):
    create_response = client.post(
        "/patients/",
        json={
            "name": "Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    patient_id = create_response.json()["patient_id"]

    response = client.get(f"/patients/{patient_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient_id
    assert data["name"] == "Test Patient"


def test_get_nonexistent_patient(client):
    response = client.get("/patients/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_update_patient(client):
    create_response = client.post(
        "/patients/",
        json={
            "name": "Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    patient_id = create_response.json()["patient_id"]

    response = client.put(
        f"/patients/{patient_id}",
        json={
            "name": "Updated Patient",
            "phone": "9999999999",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient_id
    assert data["name"] == "Updated Patient"
    assert data["phone"] == "9999999999"

    # Fields not included in the update should remain unchanged.
    assert data["gender"] == "Male"
    assert data["date_of_birth"] == "2002-05-15"
    assert data["preferred_language"] == "en"


def test_update_nonexistent_patient(client):
    response = client.put(
        "/patients/999999",
        json={
            "name": "Updated Patient",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_delete_patient(client):
    create_response = client.post(
        "/patients/",
        json={
            "name": "Test Patient",
            "date_of_birth": "2002-05-15",
            "gender": "Male",
            "phone": "9876543210",
            "preferred_language": "en",
        },
    )

    patient_id = create_response.json()["patient_id"]

    response = client.delete(f"/patients/{patient_id}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/patients/{patient_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Patient not found"


def test_delete_nonexistent_patient(client):
    response = client.delete("/patients/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_create_patient_with_default_language(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Default Language Patient",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["preferred_language"] == "en"


def test_create_patient_missing_name(client):
    response = client.post(
        "/patients/",
        json={
            "gender": "Male",
        },
    )

    assert response.status_code == 422