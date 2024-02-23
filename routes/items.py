from flask import Blueprint, request, jsonify
from routes.authorization import validate_authorization
from models import CodebeamerEntityReference, Item, Tracker, Association, Transition, User, db, Field
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
        "status": {"id": item.status.id, "name": item.status.name, "type": item.status.type},
        "storyPoints": item.storyPoints,
        "teams": [{"id": team.id, "name": team.name, "type": team.type} for team in item.teams],
        "version": 1,
        "owners": [{"id": owner.id, "name": owner.name, "email": owner.email} for owner in item.owners]
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
        summary_match = re.search(r"Summary LIKE '(.*?)'", queryString)
        if summary_match:
            summary = summary_match.group(1)
            items = Item.query.filter(Item.name.ilike(summary), Item.tracker_id == trackerId).all()
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
            "status": {"id": item.status.id, "name": item.status.name, "type": item.status.type},
            "storyPoints": item.storyPoints,
            "teams": [{"id": team.id, "name": team.name, "type": team.type} for team in item.teams],
            "version": 1,
            "owners": [{"id": owner.id, "name": owner.name, "email": owner.email} for owner in item.owners]
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
    return jsonify({
    "editableFields": [
        {
            "fieldId": field.id,
            "name": field.name,
            "type": field.type,
            "values": [
                {"id": value.id, "name": value.name, "type": value.type}
                for value in field.values
            ],
        }
        for field in fields
    ]
})


@item_bp.route('/<int:id>/fields', methods=['PUT'])
@validate_authorization
def update_item_fields(id):
    item = Item.query.get_or_404(id)
    payload = request.get_json()
    fieldValues = payload.get('fieldValues')

    for field in fieldValues:
        if 'value' in field and field['value']:
            setattr(item, field['name'], field['value'])
        elif 'values' in field:
            # go trough list of values and and get each user with 'id' and then set item assignedTo to that user
            dataToSet = []
            fieldsToSet = []
            for fieldValue in field['values']:
                if fieldValue['type'] == 'UserReference':
                    # assignedTo change
                    user = User.query.get_or_404(fieldValue['id'])
                    dataToSet.append(user)
                    entity_reference = CodebeamerEntityReference.query.get(fieldValue['id'])
                    fieldsToSet.append(entity_reference)
                elif fieldValue['type'] == 'TrackerItemReference':
                    # teams change
                    team = CodebeamerEntityReference.query.get_or_404(fieldValue['id'])
                    dataToSet.append(team)
                    fieldsToSet.append(team)


            setattr(item, field['name'], dataToSet)

           # update field
            field_instance = Field.query.filter_by(itemId=id, name=field['name']).first()
            # Access the values attribute to get associated CodebeamerEntityReference instances
            field_instance.values = fieldsToSet

           
                            

    

    db.session.commit()
    return jsonify({"message": "Item fields updated successfully"})

@item_bp.route('/<int:id>/transitions', methods=['GET'])
@validate_authorization
def get_item_transitions(id):
    item = Item.query.get_or_404(id)
    # get transition that have from_status_id = item.status_id
    transitions = Transition.query.filter_by(from_status_id=item.status_id).all()
    # for each transition get to_status_id and then get status with that id
    transitions_data = [
        {
            "id": transition.id,
            "name": transition.name,
            "fromStatus": {
                "id": transition.from_status.id,
                "name": transition.from_status.name,
                "type": transition.from_status.type
            },
            "toStatus": {
                "id": transition.to_status.id,
                "name": transition.to_status.name,
                "type": transition.to_status.type
            }
        }
        for transition in transitions
    ]

    return jsonify(transitions_data)