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
@app.route('/get_tickets', defaults={'offset_val': 0, 'filter_name': None, 'value': None}, methods=['GET'])
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
                tickets = session.query(Ticket).filter(Ticket.status==Status(value) and not Ticket.is_deleted).offset(offset_val).limit(TICKETS_LIMIT).all()
            elif filter_name == 'user' and len(value)>0:
                tickets = session.query(Ticket).filter(Ticket.created_by==value and not Ticket.is_deleted).offset(offset_val).limit(TICKETS_LIMIT).all()
            else:                
                tickets = session.query(Ticket).filter(not Ticket.is_deleted).offset(offset_val).limit(TICKETS_LIMIT).all()
            
            data = ticket_to_json(tickets)
            return data, 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
@app.route('/update/<column_name>/<id>/<new_value>', methods=['POST'])
def handle_update(column_name, id, new_value):
    """
        Update the status or description of tickets
    """
    if request.method == 'POST':
        try:
            if column_name != None and id != None and new_value != None:
                ticket = session.query(Ticket).filter(Ticket.id==id).first()

                if column_name == 'status':
                    ticket.status = Status(new_value)
                if column_name == 'description':
                    ticket.description = new_value
                    
                session.commit()
                return jsonify({'message': f"Column {column_name}, with id: {id}, is changed."}), 200
            else:
                return jsonify({'error': 'send a valid column name, id and the new value to update.'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:id>/del', defaults={'hard_delete': True}, methods=['DELETE'])
@app.route('/delete/<int:id>', defaults={'hard_delete': False}, methods=['DELETE'])
def handle_delete(id, hard_delete):
        if request.method == 'DELETE':
            try:
                if id>0 :
                    ticket = session.query(Ticket).get(id)
                    
                    if hard_delete:
                        session.delete(ticket)
                    else:
                        ticket.is_deleted = True
                    
                    session.commit()
                    
                    return jsonify({'message': f'deleted ticket with id: {id}'}), 200
                else:
                    return jsonify({'error': 'id is invalid'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
if __name__ == "__main__":
    app.run()