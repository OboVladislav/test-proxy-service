def test_get_profile_success(client, registered_user, auth_headers):
    resp = client.get("/api/profile", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == registered_user["email"]
    assert "activation_key" in data
    assert "vm" in data


def test_get_profile_unauthorized(client):
    resp = client.get("/api/profile")
    assert resp.status_code == 401


def test_get_profile_invalid_token(client):
    resp = client.get("/api/profile", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


def test_refresh_key_changes_key(client, registered_user, auth_headers):
    old_key = client.get("/api/profile", headers=auth_headers).json()["activation_key"]

    client.post("/api/profile/refresh-key", headers=auth_headers)

    new_key = client.get("/api/profile", headers=auth_headers).json()["activation_key"]
    assert new_key is not None
    assert new_key != old_key


def test_refresh_key_unauthorized(client):
    resp = client.post("/api/profile/refresh-key")
    assert resp.status_code == 401


def test_change_password_success(client, registered_user, auth_headers):
    resp = client.post("/api/profile/change-password", headers=auth_headers, json={
        "old_password": registered_user["password"],
        "new_password": "newpassword456",
    })
    assert resp.status_code == 200

    login = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": "newpassword456",
    })
    assert login.status_code == 200


def test_change_password_wrong_old(client, registered_user, auth_headers):
    resp = client.post("/api/profile/change-password", headers=auth_headers, json={
        "old_password": "wrongpassword",
        "new_password": "newpassword456",
    })
    assert resp.status_code == 400


def test_change_password_old_invalid_after_change(client, registered_user, auth_headers):
    client.post("/api/profile/change-password", headers=auth_headers, json={
        "old_password": registered_user["password"],
        "new_password": "newpassword456",
    })
    login = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert login.status_code == 401


def test_disconnect_frees_vm(client, registered_user, auth_headers, vm, db):
    from app.models.user import User
    from app.models.vm import VirtualMachine

    user = db.query(User).filter(User.email == registered_user["email"]).first()
    client.post("/api/activate-key", json={"activation_key": user.activation_key})

    db.refresh(vm)
    assert vm.current_user_id is not None

    client.post("/api/disconnect", headers=auth_headers)

    db.refresh(vm)
    assert vm.current_user_id is None


def test_disconnect_without_vm_ok(client, auth_headers):
    resp = client.post("/api/disconnect", headers=auth_headers)
    assert resp.status_code == 200


def test_disconnect_unauthorized(client):
    resp = client.post("/api/disconnect")
    assert resp.status_code == 401
