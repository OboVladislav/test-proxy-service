import secrets

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.tasks.email_tasks import send_activation_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(400, "User already exists")

    activation_key = secrets.token_hex(16)

    user = User(
        email=data.email,
        password=hash_password(data.password),
        activation_key=activation_key,
    )

    db.add(user)
    db.commit()

    send_activation_email.delay(data.email, activation_key)

    return {"message": "registered"}


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
    }