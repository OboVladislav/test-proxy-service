def test_activate_key_success(client, registered_user, vm, db):
    from app.models.user import User
    user = db.query(User).filter(User.email == registered_user["email"]).first()

    resp = client.post("/api/activate-key", json={"activation_key": user.activation_key})
    assert resp.status_code == 200

    data = resp.json()
    assert "access_token" in data
    assert "user_id" in data
    assert data["host"] == vm.host
    assert data["port"] == vm.port
    assert data["protocol"] == vm.protocol


def test_activate_key_consumes_key(client, registered_user, vm, db):
    from app.models.user import User
    user = db.query(User).filter(User.email == registered_user["email"]).first()
    key = user.activation_key

    client.post("/api/activate-key", json={"activation_key": key})

    db.refresh(user)
    assert user.activation_key is None


def test_activate_key_assigns_vm(client, registered_user, vm, db):
    from app.models.user import User
    user = db.query(User).filter(User.email == registered_user["email"]).first()

    client.post("/api/activate-key", json={"activation_key": user.activation_key})

    db.refresh(vm)
    db.refresh(user)
    assert vm.current_user_id == user.id
    assert vm.last_used_at is not None


def test_activate_key_invalid(client):
    resp = client.post("/api/activate-key", json={"activation_key": "invalid_key_000"})
    assert resp.status_code == 404


def test_activate_key_no_free_vm(client, registered_user, db):
    from app.models.user import User
    user = db.query(User).filter(User.email == registered_user["email"]).first()
    # нет VM в базе → 503
    resp = client.post("/api/activate-key", json={"activation_key": user.activation_key})
    assert resp.status_code == 503


def test_activate_key_already_used(client, registered_user, vm, db):
    from app.models.user import User
    user = db.query(User).filter(User.email == registered_user["email"]).first()
    key = user.activation_key

    client.post("/api/activate-key", json={"activation_key": key})
    resp = client.post("/api/activate-key", json={"activation_key": key})
    assert resp.status_code == 404
