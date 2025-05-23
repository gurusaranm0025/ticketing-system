from flask import jsonify
from db import Ticket

from typing import List

def ticket_to_json(tickets: List[Ticket]):
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
        }
        data.append(ticket_data)
    return jsonify(data)