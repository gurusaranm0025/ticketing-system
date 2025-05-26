from flask import Flask, request, jsonify

# local imports
from db import get_session, Tickets, Status, Engineers, Tags
from methods import ticket_to_json

TICKETS_LIMIT = 5
 
app = Flask(__name__)
session = get_session()

@app.route('/new_ticket', methods=['POST'])
def new_ticket():
    """
        Create a new ticket.
        
        Incoming JSON Structure:
            {
                title: string,
                description: string,
                status: string,
                created_by: string -> will change to user or engineer id,
                engineer_ids: list[int] => list[engineers.id],
                tag_ids: list[int] => list[tags.id],
            }
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            if len(data["engineer_ids"])>0:
                engineers = session.query(Engineers).filter(Engineers.id.in_(data["engineer_ids"])).all()
            else:
                engineers = []

            if len(data["tag_ids"])>0:            
                tags = session.query(Tags).filter(Tags.id.in_(data["tag_ids"])).all()
            else:
                tags = []

            ticket = Tickets(
                title=data['title'], 
                description=data['description'], 
                status=Status(data['status']), 
                created_by=data['created_by'],
                engineers=engineers,
                tags=tags
            )
            
            session.add(ticket)
            session.commit()
            return jsonify({"message": 'new ticket added'}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/get_tickets', defaults={'offset_val': 0, 'filter_name': None, 'value': None}, methods=['GET'])
@app.route('/get_tickets/<string:filter_name>/<string:value>', defaults={'offset_val': 0}, methods=['GET'])
@app.route('/get_tickets/<string:filter_name>/<string:value>/<int:offset_val>', methods=['GET'])
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
            if filter_name == None or value == None: # rethink this approach for checking the if both values are present
                filter_name, value = None, None
                
            if filter_name == 'status' and len(value)>0:
                tickets = session.query(Tickets).filter(Tickets.status==Status(value) and Tickets.is_deleted==False).offset(offset_val).limit(TICKETS_LIMIT).all()
            elif filter_name == 'user' and len(value)>0:
                tickets = session.query(Tickets).filter(Tickets.created_by==value and Tickets.is_deleted==False).offset(offset_val).limit(TICKETS_LIMIT).all()
            else:                
                tickets = session.query(Tickets).filter(Tickets.is_deleted==False).offset(offset_val).limit(TICKETS_LIMIT).all()
            
            print(tickets[0])
            data = ticket_to_json(tickets)
            # print(data)
            return data, 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
@app.route('/update/<string:column_name>/<int:id>/<string:new_value>', methods=['POST'])
def handle_update(column_name, id, new_value):
    """
        Update the status or description of tickets
    """
    if request.method == 'POST':
        try:
            if column_name != None and id != None and new_value != None:
                ticket = session.query(Tickets).filter(Tickets.id==id and Tickets.is_deleted==False).first()

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
    """
        Delete any ticket.
        (Fixed this ==> This endpoint allows hard delete of soft deleted items)
    """
    if request.method == 'DELETE':
        try:
            # if id>0 :
                ticket = session.query(Tickets).filter(Tickets.is_deleted==False).get(id)
                
                if hard_delete:
                    session.delete(ticket)
                else:
                    ticket.is_deleted = True
                
                session.commit()
                
                return jsonify({'message': f'deleted ticket with id: {id}'}), 200
            # else:
            #     return jsonify({'error': 'id is invalid'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route("/add_engineer", methods=['POST'])
def add_engineer():
    if request.method == 'POST':
        try:
            data = request.get_json()
            engineer = Engineers(name=data['name'], role=data["role"])
            
            session.add(engineer)
            session.commit()
            return jsonify({'message': 'added engineer successfully.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route("/add_tag", methods=['POST'])
def add_tag():
    if request.method == 'POST':
        try:
            data = request.get_json()
            tag = Tags(name=data["name"], description=data["description"])
            
            session.add(tag)
            session.commit()
            return jsonify({'message': 'added tag successfully.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
                
if __name__ == "__main__":
    app.run(debug=True)