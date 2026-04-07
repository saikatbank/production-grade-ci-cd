def test_create_item(client):
    response = client.post(
        "/api/v1/items/", json={"title": "Test Item", "description": "This is a test"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "This is a test"
    assert "id" in data


def test_read_items(client):
    client.post(
        "/api/v1/items/",
        json={"title": "Test Item 2", "description": "This is a another test"},
    )

    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["title"] == "Test Item 2" for item in data)


def test_read_nonexistent_item(client):
    response = client.get("/api/v1/items/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
