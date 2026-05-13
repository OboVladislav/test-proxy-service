import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import patch

import app.db.database as db_module

DATABASE_URL = "sqlite://"


@pytest.fixture
def engine():
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def db(engine):
    from app.db.database import Base
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db, engine):
    from app.main import app
    from app.db.database import get_db

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with patch.object(db_module, "engine", engine), \
         patch("app.db.init_db.seed"), \
         patch("app.tasks.email_tasks.send_activation_email"):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    client.post("/auth/register", json={"email": "user@test.com", "password": "password123"})
    return {"email": "user@test.com", "password": "password123"}


@pytest.fixture
def auth_headers(client, registered_user):
    resp = client.post("/auth/login", json=registered_user)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def vm(db):
    from app.models.vm import VirtualMachine
    vm = VirtualMachine(name="proxy-1", host="10.0.0.1", port=1080, protocol="socks5")
    db.add(vm)
    db.commit()
    db.refresh(vm)
    return vm
