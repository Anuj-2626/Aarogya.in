from datetime import datetime

from Backend.app.models import (
    Patient,
    Session as ClinicalSession,
    TimelineEvent,
)
from Backend.app.services.timeline_service import (
    VALID_EVENT_TYPES,
    VALID_SOURCE_TYPES,
    create_timeline_event,
    get_patient_timeline,
    get_timeline_event,
)


def create_patient(client):
    response = client.post(
        "/patients/",
        json={
            "name": "Timeline Test Patient",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "phone": "9999999999",
            "preferred_language": "en",
        },
    )

    assert response.status_code == 201

    return response.json()["patient_id"]


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

    return response.json()["session_id"]


def create_timeline_event_api(
    client,
    patient_id,
    session_id,
    event_date="2026-08-12T10:00:00",
    event_type="diagnosis",
    title="Diagnosis: Diabetes",
    description="Patient reported history of diabetes.",
    source_type="interview",
    source_id=1,
    structured_data='{"severity": "moderate"}',
):
    return client.post(
        "/timeline/events",
        json={
            "patient_id": patient_id,
            "session_id": session_id,
            "event_date": event_date,
            "event_type": event_type,
            "title": title,
            "description": description,
            "source_type": source_type,
            "source_id": source_id,
            "structured_data": structured_data,
        },
    )


def test_create_timeline_event(client):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    response = create_timeline_event_api(
        client,
        patient_id,
        session_id,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient_id
    assert data["session_id"] == session_id
    assert data["event_type"] == "diagnosis"
    assert data["title"] == "Diagnosis: Diabetes"
    assert data["source_type"] == "interview"
    assert data["source_id"] == 1
    assert data["structured_data"] == (
        '{"severity": "moderate"}'
    )


def test_create_timeline_event_without_session(
    client
):
    patient_id = create_patient(client)

    response = create_timeline_event_api(
        client,
        patient_id,
        session_id=None,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient_id
    assert data["session_id"] is None


def test_create_timeline_event_rejects_nonexistent_patient(
    client
):
    response = create_timeline_event_api(
        client,
        patient_id=999999,
        session_id=None,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Patient not found"
    )


def test_create_timeline_event_rejects_nonexistent_session(
    client
):
    patient_id = create_patient(client)

    response = create_timeline_event_api(
        client,
        patient_id=patient_id,
        session_id=999999,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Session not found"
    )


def test_create_timeline_event_rejects_session_from_different_patient(
    client
):
    patient_one_id = create_patient(client)

    patient_two_response = client.post(
        "/patients/",
        json={
            "name": "Second Timeline Patient",
            "date_of_birth": "1999-01-01",
            "gender": "Female",
            "phone": "8888888888",
            "preferred_language": "en",
        },
    )

    assert patient_two_response.status_code == 201

    patient_two_id = patient_two_response.json()[
        "patient_id"
    ]

    session_two_id = create_session(
        client,
        patient_two_id
    )

    response = create_timeline_event_api(
        client,
        patient_id=patient_one_id,
        session_id=session_two_id,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Session does not belong to the specified patient"
    )


def test_create_timeline_event_rejects_invalid_event_type(
    client
):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    response = create_timeline_event_api(
        client,
        patient_id,
        session_id,
        event_type="invalid_event",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid event type: invalid_event"
    )


def test_create_timeline_event_rejects_invalid_source_type(
    client
):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    response = create_timeline_event_api(
        client,
        patient_id,
        session_id,
        source_type="invalid_source",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid source type: invalid_source"
    )


def test_create_timeline_event_rejects_invalid_structured_json(
    client
):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    response = create_timeline_event_api(
        client,
        patient_id,
        session_id,
        structured_data="{invalid json",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "structured_data must contain valid JSON"
    )


def test_create_timeline_event_accepts_valid_event_types(
    client
):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    for event_type in VALID_EVENT_TYPES:
        response = create_timeline_event_api(
            client,
            patient_id,
            session_id,
            event_type=event_type,
        )

        assert response.status_code == 200
        assert response.json()["event_type"] == event_type


def test_create_timeline_event_accepts_valid_source_types(
    client
):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    for source_type in VALID_SOURCE_TYPES:
        response = create_timeline_event_api(
            client,
            patient_id,
            session_id,
            source_type=source_type,
        )

        assert response.status_code == 200
        assert response.json()["source_type"] == source_type


def test_get_timeline_event(client):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    create_response = create_timeline_event_api(
        client,
        patient_id,
        session_id,
    )

    event_id = create_response.json()["event_id"]

    response = client.get(
        f"/timeline/events/{event_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_id"] == event_id
    assert data["patient_id"] == patient_id
    assert data["session_id"] == session_id


def test_get_nonexistent_timeline_event(client):
    response = client.get(
        "/timeline/events/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Timeline event not found"
    )


def test_get_patient_timeline(client):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    create_timeline_event_api(
        client,
        patient_id,
        session_id,
        event_date="2026-08-10T10:00:00",
        title="First Event",
    )

    create_timeline_event_api(
        client,
        patient_id,
        session_id,
        event_date="2026-08-12T10:00:00",
        title="Second Event",
    )

    response = client.get(
        f"/timeline/patient/{patient_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient_id
    assert data["total_events"] == 2
    assert len(data["events"]) == 2


def test_patient_timeline_is_ordered_by_event_date(
    client
):
    patient_id = create_patient(client)
    session_id = create_session(
        client,
        patient_id
    )

    create_timeline_event_api(
        client,
        patient_id,
        session_id,
        event_date="2026-08-20T10:00:00",
        title="Later Event",
    )

    create_timeline_event_api(
        client,
        patient_id,
        session_id,
        event_date="2026-08-10T10:00:00",
        title="Earlier Event",
    )

    create_timeline_event_api(
        client,
        patient_id,
        session_id,
        event_date="2026-08-15T10:00:00",
        title="Middle Event",
    )

    response = client.get(
        f"/timeline/patient/{patient_id}"
    )

    assert response.status_code == 200

    events = response.json()["events"]

    assert [
        event["title"]
        for event in events
    ] == [
        "Earlier Event",
        "Middle Event",
        "Later Event",
    ]


def test_patient_timeline_only_returns_events_for_requested_patient(
    client
):
    patient_one_id = create_patient(client)

    patient_two_response = client.post(
        "/patients/",
        json={
            "name": "Another Patient",
            "date_of_birth": "1998-01-01",
            "gender": "Female",
            "phone": "7777777777",
            "preferred_language": "en",
        },
    )

    assert patient_two_response.status_code == 201

    patient_two_id = patient_two_response.json()[
        "patient_id"
    ]

    session_one_id = create_session(
        client,
        patient_one_id
    )

    session_two_id = create_session(
        client,
        patient_two_id
    )

    create_timeline_event_api(
        client,
        patient_one_id,
        session_one_id,
        title="Patient One Event",
    )

    create_timeline_event_api(
        client,
        patient_two_id,
        session_two_id,
        title="Patient Two Event",
    )

    response = client.get(
        f"/timeline/patient/{patient_one_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 1
    assert data["events"][0]["title"] == (
        "Patient One Event"
    )


def test_get_patient_timeline_rejects_nonexistent_patient(
    client
):
    response = client.get(
        "/timeline/patient/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Patient not found"
    )


def test_create_timeline_event_service(
    db_session
):
    patient = Patient(
        name="Service Test Patient",
        preferred_language="en",
    )

    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    event = create_timeline_event(
        db=db_session,
        patient_id=patient.patient_id,
        session_id=None,
        event_date=datetime(2026, 8, 12, 10, 0, 0),
        event_type="symptom",
        title="Symptom: Headache",
        description="Patient reported headache.",
        source_type="interview",
        source_id=10,
        structured_data='{"duration": "2 days"}',
    )

    assert event.event_id is not None
    assert event.patient_id == patient.patient_id
    assert event.session_id is None
    assert event.event_type == "symptom"
    assert event.title == "Symptom: Headache"
    assert event.source_type == "interview"
    assert event.source_id == 10
    assert event.structured_data == (
        '{"duration": "2 days"}'
    )


def test_get_timeline_event_service(
    db_session
):
    patient = Patient(
        name="Service Retrieval Patient",
        preferred_language="en",
    )

    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    event = create_timeline_event(
        db=db_session,
        patient_id=patient.patient_id,
        session_id=None,
        event_date=datetime(2026, 8, 12, 10, 0, 0),
        event_type="medication",
        title="Medication: Metformin",
        description="Current medication.",
        source_type="system",
        source_id=20,
        structured_data=None,
    )

    retrieved = get_timeline_event(
        db=db_session,
        event_id=event.event_id
    )

    assert retrieved is not None
    assert retrieved.event_id == event.event_id
    assert retrieved.title == "Medication: Metformin"


def test_get_timeline_event_service_returns_none_for_missing_event(
    db_session
):
    result = get_timeline_event(
        db=db_session,
        event_id=999999
    )

    assert result is None


def test_get_patient_timeline_service(
    db_session
):
    patient = Patient(
        name="Timeline Service Patient",
        preferred_language="en",
    )

    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    create_timeline_event(
        db=db_session,
        patient_id=patient.patient_id,
        session_id=None,
        event_date=datetime(2026, 8, 20, 10, 0, 0),
        event_type="diagnosis",
        title="Later Diagnosis",
        description=None,
        source_type="system",
        source_id=None,
        structured_data=None,
    )

    create_timeline_event(
        db=db_session,
        patient_id=patient.patient_id,
        session_id=None,
        event_date=datetime(2026, 8, 10, 10, 0, 0),
        event_type="symptom",
        title="Earlier Symptom",
        description=None,
        source_type="interview",
        source_id=1,
        structured_data=None,
    )

    events = get_patient_timeline(
        db=db_session,
        patient_id=patient.patient_id
    )

    assert len(events) == 2

    assert events[0].title == "Earlier Symptom"
    assert events[1].title == "Later Diagnosis"


def test_get_patient_timeline_service_rejects_missing_patient(
    db_session
):
    try:
        get_patient_timeline(
            db=db_session,
            patient_id=999999
        )
    except ValueError as error:
        assert str(error) == "Patient not found"
    else:
        raise AssertionError(
            "Expected ValueError was not raised"
        )