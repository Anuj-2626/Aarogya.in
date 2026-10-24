def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "SIH Project backend is running"
    }


def test_test_database_is_isolated(client):
    response = client.get("/patients")

    assert response.status_code == 200