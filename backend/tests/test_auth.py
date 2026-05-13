def test_register_success(client):
    resp = client.post("/auth/register", json={"email": "new@test.com", "password": "pass123"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "registered"}


def test_register_creates_activation_key(client, db):
    from app.models.user import User
    client.post("/auth/register", json={"email": "keyed@test.com", "password": "pass"})
    user = db.query(User).filter(User.email == "keyed@test.com").first()
    assert user is not None
    assert user.activation_key is not None
    assert len(user.activation_key) == 32  # token_hex(16) → 32 символа


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "pass"})
    resp = client.post("/auth/register", json={"email": "dup@test.com", "password": "pass"})
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_register_invalid_email(client):
    resp = client.post("/auth/register", json={"email": "not-an-email", "password": "pass"})
    assert resp.status_code == 422


def test_login_success(client, registered_user):
    resp = client.post("/auth/login", json=registered_user)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/auth/login", json={"email": "ghost@test.com", "password": "pass"})
    assert resp.status_code == 401


def test_login_returns_valid_token(client, registered_user):
    from jose import jwt
    from app.core.config import settings

    resp = client.post("/auth/login", json=registered_user)
    token = resp.json()["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "sub" in payload
    assert "exp" in payload
