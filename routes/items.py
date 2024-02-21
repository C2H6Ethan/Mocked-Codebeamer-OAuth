from flask import Blueprint, request, jsonify
from routes.authorization import validate_authorization
from models import Item, Tracker, Association, db, Field
import re

item_bp = Blueprint('items', __name__)

@item_bp.route('/<int:id>', methods=['GET'])
@validate_authorization
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify({
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "descriptionFormat": item.descriptionFormat,
        "assignedTo": [{"id": user.id, "name": user.name, "email": user.email} for user in item.assignedTo],
        "tracker" : {"id": item.tracker.id, "name": item.tracker.name},
        "customFields": [{"type": customField.type, "value": customField.value} for customField in item.customFields],
        "status": [{"id": status.id, "name": status.name, "type": status.type} for status in item.status],
        "storyPoints": item.storyPoints
    })

@item_bp.route('/query', methods=['POST'])
@validate_authorization
def query_items():
    payload = request.get_json()
    queryString = payload.get('queryString')
 

    trackerId = int(queryString.split(' ')[2].replace('(', '').replace(')', ''))
    item_ids_match = re.search(r'item\.id\s+IN\s+\(([\d\s,]+)\)', queryString)

    tracker = Tracker.query.get_or_404(trackerId)
    items = []
    if item_ids_match:
        # Extracted item IDs string
        itemIdsString = item_ids_match.group(1)

        # Convert the item IDs string to a list of integers
        itemIds = [int(id.strip()) for id in itemIdsString.split(',')]

        items = Item.query.filter(Item.id.in_(itemIds), Item.tracker_id == trackerId).all()
    else:
        items = Item.query.filter_by(tracker_id=trackerId).all()

    item_data = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "descriptionFormat": item.descriptionFormat,
            "assignedTo": [{"id": user.id, "name": user.name, "email": user.email} for user in item.assignedTo],
            "tracker" : {"id": tracker.id, "name": tracker.name},
            "customFields": [{"type": customField.type, "value": customField.value} for customField in item.customFields],
            "status": [{"id": status.id, "name": status.name, "type": status.type} for status in item.status],
            "storyPoints": item.storyPoints
        }
        for item in items
    ]

    return_data = {
        "page": 1,
        "pageSize": 13,
        "total": len(item_data),
        "items": item_data
    }
    return jsonify(return_data)

@item_bp.route('/<int:id>/relations', methods=['GET'])
@validate_authorization
def item_relations(id):
    item = Item.query.get_or_404(id)
    #get all Associations where from_entity.id = item.id
    associations = Association.query.filter_by(from_id=item.id).all()

    downstreamReferences = [association for association in associations if association.type.name == "DownstreamTrackerItemReference"]
    downstreamReferences_data = [
        {
            "id": association.id,
            "itemRevision": {
                "id": association.to_id
            },
            "type": 'downstream'
        }
        for association in downstreamReferences
    ]

    outgoingAssociations = [association for association in associations if association.type.name == "OutgoingTrackerItemAssociation"]
    outgoingAssociations_data = [
        {
            "id": association.id,
            "itemRevision": {
                "id": association.to_id
            },
            "type": 'relation'
        }
        for association in outgoingAssociations
    ]

    relations_data = {
        "itemId": {
            "id": item.id
        },
        "downstreamReferences": downstreamReferences_data,
        "outgoingAssociations": outgoingAssociations_data
    }
    
    return jsonify(relations_data)

# Fields
@item_bp.route('/<int:id>/fields', methods=['GET'])
@validate_authorization
def get_item_fields(id):
    fields = Field.query.filter_by(itemId=id).all()
    return jsonify({ "editableFields": [{"fieldId": field.id, "name": field.name, "type": field.type} for field in fields]})

@item_bp.route('/<int:id>/fields', methods=['PUT'])
@validate_authorization
def update_item_fields(id):
    item = Item.query.get_or_404(id)
    payload = request.get_json()
    fieldValues = payload.get('fieldValues')

    for field in fieldValues:
        setattr(item, field['name'], field['value'])
    

    db.session.commit()
    return jsonify({"message": "Item fields updated successfully"})