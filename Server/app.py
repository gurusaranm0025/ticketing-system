from flask import Flask, request, jsonify

# local imports
from db import get_session, Ticket, Status
from methods import ticket_to_json

TICKETS_LIMIT = 5
 
app = Flask(__name__)
session = get_session()
    
@app.route('/new_ticket', methods=['POST'])
def new_ticket():
    """
        Create a new ticket
    """
    if request.method == 'POST':
        try:
            request_data = request.get_json()

            ticket = Ticket(
                title=request_data['title'], 
                description=request_data['description'], 
                status=Status(request_data['status']), 
                created_by=request_data['created_by']
            )
            
            session.add(ticket)
            session.commit()
            return jsonify({"message": 'new ticket added'}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/get_tickets/<offset_val>/<filter_name>/<value>', methods=['GET'])
def get_tickets(offset_val, filter_name, value):
    """
        Get and read tickets.
        Filter through based on their status and who created the ticket.
        Decide how many rows you want to query.
    """
    if request.method == 'GET':
        try:
            if offset_val == None:
                offset_val = 0
            if filter_name == None or value == None:
                filter_name, value = None, None
                
            if filter_name == 'status' and len(value)>0:
                tickets = session.query(Ticket).filter(Ticket.status== Status(value)).offset(offset_val).limit(TICKETS_LIMIT).all()
            elif filter_name == 'user' and len(value)>0:
                tickets = session.query(Ticket).filter(Ticket.created_by==value).offset(offset_val).limit(TICKETS_LIMIT).all()
            else:                
                tickets = session.query(Ticket).offset(offset_val).limit(TICKETS_LIMIT).all()
            
            data = ticket_to_json(tickets)
            return data, 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
# @app.route('/update')
# def update():
#     stmt = Ticket.
    
        
if __name__ == "__main__":
    app.run()