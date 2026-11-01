def register_and_login(client, username="harsh", password="test1234"):
    """Helper: create a user, log in, return the Authorization header."""
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", data={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Task API"}


def test_register_user(client):
    response = client.post("/register", json={"username": "harsh", "password": "test1234"})
    assert response.status_code == 200
    assert response.json()["username"] == "harsh"
    assert "password" not in response.json()          # never return passwords


def test_register_duplicate_username(client):
    client.post("/register", json={"username": "harsh", "password": "test1234"})
    response = client.post("/register", json={"username": "harsh", "password": "other"})
    assert response.status_code == 400


def test_login_success(client):
    client.post("/register", json={"username": "harsh", "password": "test1234"})
    response = client.post("/login", data={"username": "harsh", "password": "test1234"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/register", json={"username": "harsh", "password": "test1234"})
    response = client.post("/login", data={"username": "harsh", "password": "wrong"})
    assert response.status_code == 401


def test_tasks_require_login(client):
    response = client.get("/tasks")
    assert response.status_code == 401


def test_create_and_list_tasks(client):
    headers = register_and_login(client)
    created = client.post("/tasks", json={"title": "Learn pytest"}, headers=headers)
    assert created.status_code == 200
    assert created.json()["title"] == "Learn pytest"
    assert created.json()["done"] is False

    listed = client.get("/tasks", headers=headers)
    assert len(listed.json()) == 1


def test_get_task_not_found(client):
    headers = register_and_login(client)
    response = client.get("/tasks/999", headers=headers)
    assert response.status_code == 404


def test_update_task(client):
    headers = register_and_login(client)
    task = client.post("/tasks", json={"title": "Old title"}, headers=headers).json()

    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "New title", "done": True},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["done"] is True


def test_delete_task(client):
    headers = register_and_login(client)
    task = client.post("/tasks", json={"title": "Temporary"}, headers=headers).json()

    response = client.delete(f"/tasks/{task['id']}", headers=headers)
    assert response.status_code == 200

    after = client.get(f"/tasks/{task['id']}", headers=headers)
    assert after.status_code == 404


def test_user_cannot_see_another_users_task(client):
    harsh = register_and_login(client, "harsh", "test1234")
    asha = register_and_login(client, "asha", "test1234")

    task = client.post("/tasks", json={"title": "Private"}, headers=harsh).json()

    assert client.get("/tasks", headers=asha).json() == []
    assert client.get(f"/tasks/{task['id']}", headers=asha).status_code == 404