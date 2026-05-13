from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.vm import VirtualMachine


vms = [
    {"name": "proxy-1", "host": "10.0.0.1", "port": 1080, "protocol": "socks5"},
    {"name": "proxy-2", "host": "10.0.0.2", "port": 1080, "protocol": "socks5"},
]


def seed():
    db: Session = SessionLocal()
    try:
        if db.query(VirtualMachine).first():
            return
        for vm_data in vms:
            db.add(VirtualMachine(**vm_data))
        db.commit()
    finally:
        db.close()