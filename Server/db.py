from sqlalchemy import create_engine, Column, Integer, String, Enum, Boolean, Table, ForeignKey
# from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

import json
import enum
import datetime

engine = create_engine('sqlite:///./instance/site.db')
Base = declarative_base()

class Status(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    
tickets_tags = Table(
    'tickets_tags',
    Base.metadata,
    Column('ticket_id', ForeignKey('tickets.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

engineers_tags = Table(
    'engineers_tags',
    Base.metadata,
    Column('engineer_id', ForeignKey('engineers.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

tickets_engineers = Table(
    'tickets_engineers',
    Base.metadata,
    Column('ticket_id', ForeignKey('tickets.id'), primary_key=True),
    Column('engineer_id', ForeignKey('engineers.id'), primary_key=True)
)

class Tickets(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(400), nullable=False)
    status = Column(Enum(Status), nullable=False)
    created_by = Column(String(50), nullable=False)
    
    is_deleted = Column(Boolean, default=False)
    created_at = Column(String(20), default=datetime.datetime.now().strftime(f"%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String(20), default=datetime.datetime.now().strftime(f"%Y-%m-%d %H:%M:%S"))
    
    tags = relationship("Tags", secondary=tickets_tags, back_populates="tickets")
    engineers = relationship("Engineers", secondary=tickets_engineers, back_populates="tickets")
    
class Engineers(Base):
    __tablename__ = 'engineers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    role = Column(String(200), nullable=False)
    
    tickets = relationship("Tickets", secondary=tickets_engineers, back_populates="engineers")
    tags = relationship("Tags", secondary=engineers_tags, back_populates="engineers")
    
    # def __repr__(self):
    #     return json.dumps({
    #         "id": self.id,
    #         "name": self.name,
    #         "role": self.role,
    #         "tickets": self.tickets,
    #         "tags": self.tags
    #     })
    
class Tags(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200))
    
    tickets = relationship("Tickets", secondary=tickets_tags, back_populates="tags")
    engineers = relationship("Engineers", secondary=engineers_tags, back_populates="tags")
    
    

def get_session():
    """
        Generates session for the server.
    """
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()