from jose import jwt

from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings


def test_hash_password_differs_from_input():
    assert hash_password("mypassword") != "mypassword"


def test_hash_same_input_gives_different_hashes():
    h1 = hash_password("mypassword")
    h2 = hash_password("mypassword")
    assert h1 != h2  # bcrypt использует случайную соль


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_empty():
    hashed = hash_password("mypassword")
    assert verify_password("", hashed) is False


def test_create_access_token_contains_sub():
    token = create_access_token({"sub": "42"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "42"


def test_create_access_token_has_expiry():
    token = create_access_token({"sub": "1"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" in payload


def test_create_access_token_invalid_key():
    token = create_access_token({"sub": "1"})
    try:
        jwt.decode(token, "wrong_secret", algorithms=[settings.ALGORITHM])
        assert False, "Should have raised"
    except Exception:
        pass
