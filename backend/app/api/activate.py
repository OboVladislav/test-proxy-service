from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.database import get_db
from app.models.user import User
from app.schemas.vm import ActivateKeySchema
from app.services.vm_service import get_free_vm, assign_vm_to_user

router = APIRouter(prefix="/api", tags=["Activation"])


@router.post("/activate-key")
def activate_key(data: ActivateKeySchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.activation_key == data.activation_key
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid activation key")

    vm = get_free_vm(db)

    if not vm:
        raise HTTPException(status_code=503, detail="All proxies are busy")

    assign_vm_to_user(db, vm, user.id)

    user.activation_key = None
    db.commit()

    token = create_access_token({"sub": str(user.id)})

    return {
        "user_id": user.id,
        "access_token": token,
        "host": vm.host,
        "port": vm.port,
        "protocol": vm.protocol,
    }