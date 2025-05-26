from flask import Flask, request, jsonify
from db import get_session, Tickets, Status, Engineers, Tags

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
            
            engineers, tags = [], []
            if len(data["engineer_ids"])>0:
                engineers = session.query(Engineers).filter(Engineers.id.in_(data["engineer_ids"])).all()

            if len(data["tag_ids"])>0:            
                tags = session.query(Tags).filter(Tags.id.in_(data["tag_ids"])).all()

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
            return jsonify({"message": 'new ticket added'}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/get_tickets", methods=["GET"])
def get_tickets():
    """
        Get and read tickets.
        Filter through based on their status and who created the ticket.
        Decide how many rows you want to query.
        Input JSON format:
            {
                offset_val: int -> default: 0,
                filter_name: string -> default: None -> status, user,
                value: string -> default: None
            }
    """
    if request.method == "GET":
        try:
            data = request.get_json()
            if data["offset_val"] == None:
                data["offset_val"] = 0
            if data["filter_name"] == None or data["value"] == None: # rethink this approach for checking the if both values are present
                data["filter_name"], data["value"] = None, None
                
            if data["filter_name"] == 'status' and len(data["value"])>0:
                tickets = session.query(Tickets).filter(Tickets.status==Status(data["value"]) and Tickets.is_deleted==False).offset(data["offset_val"]).limit(TICKETS_LIMIT).all()
            elif data["filter_name"] == 'user' and len(data["value"])>0:
                tickets = session.query(Tickets).filter(Tickets.created_by==data["value"] and Tickets.is_deleted==False).offset(data["offset_val"]).limit(TICKETS_LIMIT).all()
            else:                
                tickets = session.query(Tickets).filter(Tickets.is_deleted==False).offset(data["offset_val"]).limit(TICKETS_LIMIT).all()
            
            return jsonify([ticket.to_dict() for ticket in tickets]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
@app.route("/update", methods=['PATCH'])
def handle_update():
    """
        Update the status or description of tickets.
        Input JSON Format:
            {
                column_name: string,
                ticket_id: int,
                new_value: string
            }
    """
    if request.method == "PATCH":
        try:
            data = request.get_json()
            if data["column_name"] != None and data["ticket_id"] != None and data["new_value"] != None:
                ticket = session.query(Tickets).filter(Tickets.id==data["ticket_id"] and Tickets.is_deleted==False).first()

                if data["column_name"] == "status":
                    ticket.status = Status(data["new_value"])
                if data["column_name"] == "description":
                    ticket.description = data["new_value"]
                    
                session.commit()
                return jsonify({'message': f"Column {data["column_name"]}, with id: {data["ticket_id"]}, is changed."}), 200
            else:
                return jsonify({'error': 'send a valid column name, id and the new value to update.'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route("/delete", methods=['DELETE'])
def handle_delete():
    """
        Delete any ticket.
        Input JSON:
            {
                ticket_id: int,
                hard_delete: bool -> default: False
            }
        (Fixed this ==> This endpoint allows hard delete of soft deleted items)
    """
    if request.method == "DELETE":
        try:
            data = request.get_json()
            ticket = session.query(Tickets).filter(Tickets.id==data["ticket_id"] and Tickets.is_deleted==False).first()
            
            if data["hard_delete"]:
                session.delete(ticket)
            else:
                ticket.is_deleted = True
            
            session.commit()
            
            return jsonify({"message": f'deleted ticket with id: {data["ticket_id"]}'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route("/add_engineer", methods=["POST"])
def add_engineer():
    if request.method == "POST":
        try:
            data = request.get_json()
            engineer = Engineers(name=data["name"], role=data["role"])
            
            session.add(engineer)
            session.commit()
            return jsonify({"message": "added engineer successfully."}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route("/assign_engineer", methods=["PATCH"])
def assign_engineer():
    """
        Assign new engineer to a ticket.
        Input JSON format:
            {
                ticket_id: int,
                engineer_id: int,
            }
    """
    if request.method == "PATCH":
        try:
            data = request.get_json()
            
            ticket = session.query(Tickets).filter(Tickets.id==data["ticket_id"] and Tickets.is_deleted==False).first()
            
            engineer = session.query(Engineers).filter(Engineers.id==data["engineer_id"]).first()
            
            if engineer not in ticket.engineers:
                ticket.engineers.append(engineer)
                session.commit()
                return jsonify({"message": f'added engineer {engineer.name} to ticket id: {ticket.id}.'}), 200
            else:
                return jsonify({"error": f'Ticket already assigned to this engineer.'}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/unassign_engineer", methods=["PATCH"])
def unassign_engineer():
    """
        Unassign an engineer from a ticket
        Input JSON format:
            {
                ticket_id: int,
                engineer_id: int
            }
    """
    if request.method == "PATCH":
        try:
            data = request.get_json()
            
            ticket = session.query(Tickets).filter(Tickets.id==data["ticket_id"] and Tickets.is_deleted==False).first()
            
            engineer = session.query(Engineers).filter(Engineers.id==data["engineer_id"]).first()
            
            if engineer in ticket.engineers:
                ticket.engineers.remove(engineer)
                
                return jsonify({"message": f'engineer {engineer.name} assigned to ticket with id: {ticket.id}'}), 200
            else:
                return jsonify({"error": f'engineer {engineer.name} is not assigned to this ticket.'}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/add_tag", methods=["POST"])
def add_tag():
    if request.method == "POST":
        try:
            data = request.get_json()
            tag = Tags(name=data["name"], description=data["description"])
            
            session.add(tag)
            session.commit()
            return jsonify({"message": "added tag successfully."}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route("/assign_tag_to/<string:value>", methods=["PATCH"])
def assign_tag(value):
    """
        Assign a tag
        Input JSON format:
            {
                tag_id: int,
                id: int
            }
    """
    if request.method == "PATCH":
        try:
            data = request.get_json()
            
            if value == 'ticket':
                queried_data = session.query(Tickets).filter(Tickets.id==data["id"] and Tickets.is_deleted==False).first()
            elif value == 'engineer':
                queried_data = session.query(Engineers).filter(Engineers.id==data["id"]).first()
            
            tag = session.query(Tags).filter(Tags.id==data["tag_id"]).first()
            
            if tag not in queried_data.tags:
                queried_data.tags.append(tag)
                session.commit()
                return jsonify({"message": f'tag {tag.name} is assigned.'}), 200
            else:
                return jsonify({"error": "tag already assigned"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/unassign_tag_from/<string:value>", methods=["PATCH"])
def unassign_tag(value):
    """
        Unassigns tag from ticket and engineers.
        Input JSON format:
            {
                tag_id: int,
                id: int
            }
    """
    if request.method == "PATCH":
        try:
            data = request.get_json()
            
            if value == 'ticket':
                queried_data = session.query(Tickets).filter(Tickets.id==data["id"] and Tickets.is_deleted==False).first()
            elif value == 'engineer':
                queried_data = session.query(Engineers).filter(Engineers.id==data["id"]).first()
            
            tag = session.query(Tags).filter(Tags.id==data["tag_id"]).first()
            
            if tag in queried_data.tags:
                queried_data.tags.remove(tag)
                session.commit()
                return jsonify({"message": f'removed tag: {tag.name}.'}), 200
            else:
                return jsonify({"error": f'tag: {tag.name} is not assigned here'}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
                
if __name__ == "__main__":
    app.run(debug=True)