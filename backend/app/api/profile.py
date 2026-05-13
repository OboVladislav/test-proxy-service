import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user, hash_password, verify_password
from app.db.database import get_db
from app.models.user import User
from app.models.vm import VirtualMachine
from app.schemas.auth import ChangePasswordSchema
from app.tasks.email_tasks import send_activation_email

router = APIRouter(prefix="/api", tags=["Profile"])


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vm = db.query(VirtualMachine).filter(
        VirtualMachine.current_user_id == current_user.id
    ).first()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "activation_key": current_user.activation_key,
        "vm": {
            "host": vm.host,
            "port": vm.port,
            "protocol": vm.protocol,
        } if vm else None,
    }


@router.post("/profile/refresh-key")
def refresh_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_key = secrets.token_hex(16)
    current_user.activation_key = new_key
    db.commit()
    send_activation_email.delay(current_user.email, new_key)
    return {"message": "Key refreshed, check your email"}


@router.post("/disconnect")
def disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vm = db.query(VirtualMachine).filter(
        VirtualMachine.current_user_id == current_user.id
    ).first()
    if vm:
        vm.current_user_id = None
        db.commit()
    return {"message": "Disconnected"}


@router.post("/profile/change-password")
def change_password(
    data: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Wrong current password")

    current_user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed"}