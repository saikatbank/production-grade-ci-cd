def test_liveness_check(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_readiness_check(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
