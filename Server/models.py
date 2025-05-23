from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
from sqlalchemy.sql import func

import enum
import uuid

class Status(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'CLOSED'    

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(Enum(Status), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    created_by = db.Column(db.String(50), nullable=False)
