from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.db.database import Base
from datetime import datetime


class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    host = Column(String)
    port = Column(Integer)
    protocol = Column(String)

    is_active = Column(Boolean, default=True)

    current_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    last_used_at = Column(DateTime, nullable=True)