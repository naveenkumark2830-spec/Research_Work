def test_user_creation(client):
    response = client.post("/api/v1/users", json={"display_name": "Alice Hadoop", "preferences": {"theme": "dark"}})
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    user = data["user"]
    assert user["display_name"] == "Alice Hadoop"
    assert user["user_id"].startswith("usr_")
    assert user["preferences"]["theme"] == "dark"


def test_get_user(client):
    create_res = client.post("/api/v1/users", json={"display_name": "Bob Data"})
    user_id = create_res.json()["user"]["user_id"]

    get_res = client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 200
    assert get_res.json()["user"]["user_id"] == user_id
    assert get_res.json()["user"]["display_name"] == "Bob Data"
