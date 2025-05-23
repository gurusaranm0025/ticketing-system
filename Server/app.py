from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
 

import enum

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

engine = create_engine('sqlite:///instance/site.db')
Session = sessionmaker(bind=engine)
session = Session()

conn = engine.connect()

####### MODELS
class Status(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'CLOSED'    

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(Enum(Status), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    created_by = db.Column(db.String(50), nullable=False)

# METHODS
def convert_to_json(tickets):
    data = []    
    for ticket in tickets:
        if ticket.status == Status.OPEN:
            status = 'open'
        elif ticket.status == Status.IN_PROGRESS:
            status = 'in_progress'
        elif ticket.status == Status.CLOSED:
            status = 'closed'
        data.append({"id": ticket.id, "title": ticket.title, "description": ticket.description, "status": status, "created_at": ticket.created_at, "updated_at": ticket.updated_at, "created_by": ticket.created_by})
    return jsonify(data)

    
######## ROUTES
@app.route('/get_tickets')
def handle():
    tickets = session.query(Ticket).all()
    return convert_to_json(tickets)

@app.route('/filter_tickets/<filter_column>/<value>', methods=['GET'])
def handle_filter(filter_column, value):
    if request.method == 'GET':
        if filter_column == 'status':
            if value == 'open':
                value = Status.OPEN
            elif value == 'in_progress':
                value == Status.IN_PROGRESS
            elif value == 'closed':
                value == Status.CLOSED
            tickets = session.query(Ticket).filter_by(status=value)
            return convert_to_json(tickets)
        
        if filter_column == 'user':
            tickets = session.query(Ticket).filter_by(created_by=value)
            return convert_to_json(tickets)
            
    
@app.route('/new_ticket', methods=['POST'])
def handle_post():
    if request.method == 'POST':
        data = request.get_json()
        
        status = data['status']
        if status == 'open':
            status = Status.OPEN
        elif status == 'in_progress':
            status == Status.IN_PROGRESS
        elif status == 'closed':
            status == Status.CLOSED
                
        ticket = Ticket(title=data['title'], description=data['description'], status=status, created_by=data['created_by'])
        
        db.session.add(ticket)
        db.session.commit()
        return jsonify({'message': 'added successfully'})
    
# @app.route('/update')
# def update():
#     stmt = Ticket.
    
        
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()