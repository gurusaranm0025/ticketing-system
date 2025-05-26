from flask import jsonify
from db import Tickets

from typing import List

def ticket_to_json(tickets: List[Tickets]):
    """
        Convert queried data to json
    """
    data = []
    for ticket in tickets:
        ticket_data = {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status.value,
            "created_by": ticket.created_by,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "engineers": [[engineer.id, engineer.name] for engineer in ticket.engineers],
            "tags": [[tag.id, tag.name] for tag in ticket.tags]
        }
        data.append(ticket_data)
    return jsonify(data)