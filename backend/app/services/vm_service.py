from datetime import datetime

from sqlalchemy.orm import Session

from app.models.vm import VirtualMachine
from datetime import datetime, timezone


def get_free_vm(db: Session):
    vm = db.query(VirtualMachine).filter(
        VirtualMachine.current_user_id.is_(None),
        VirtualMachine.is_active == True,
    ).first()

    return vm



def assign_vm_to_user(db: Session, vm, user_id):
    vm.current_user_id = user_id
    vm.last_used_at = datetime.now(timezone.utc)

    db.commit()