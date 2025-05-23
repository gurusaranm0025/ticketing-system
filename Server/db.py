from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import enum
import datetime

engine = create_engine('sqlite:///./instance/site.db')
Base = declarative_base()

class Status(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(400), nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_by = Column(String(50), nullable=False)
    
    created_at = Column(String(20), default=datetime.datetime.now().strftime(f"%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String(20), default=datetime.datetime.now().strftime(f"%Y-%m-%d %H:%M:%S"))
    

def get_session():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()