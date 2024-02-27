import base64
import json
from flask import Blueprint, jsonify, request
from routes.authorization import validate_authorization
from models import CodebeamerEntityReference, Item, Project, Status, Tracker, User, Field
from models import db

tracker_bp = Blueprint('trackers', __name__)

@tracker_bp.route('/<int:id>', methods=['GET'])
@validate_authorization
def tracker(id):
    tracker = Tracker.query.get_or_404(id)
    return jsonify({
        'id': tracker.id,
        'name': tracker.name,
        'keyName': tracker.keyName,
        'color': tracker.color,
        'project': {'id': tracker.project.id, 'name': tracker.project.name}
    })

@tracker_bp.route('/<int:id>/items', methods=['GET'])
@validate_authorization
def items(id):
    tracker = Tracker.query.get_or_404(id)
    items = Item.query.filter_by(tracker_id=tracker.id).all()
    items_data = [
        {
            "id": item.id,
            "name": item.name,
        }
        for item in items
    ]
    return jsonify({"page": 1, "pageSize": 13, "total": len(items_data), "items": items_data})

@tracker_bp.route('/<int:id>/schema', methods=['GET'])
@validate_authorization
def trackerSchema(id):
    rawJson = [{"id":0,"name":"ID","type":"IntegerField","hidden":False,"valueModel":"IntegerFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"id","trackerItemField":"id"},{"id":1,"name":"Tracker","type":"ReferenceField","hidden":False,"valueModel":"NotSupportedFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"tracker","trackerItemField":"tracker"},{"id":2,"name":"Priority","type":"OptionChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<ChoiceOptionReference>","title":"P","mandatoryInStatuses":[],"multipleValues":False,"options":[{"id":0,"name":"Unset","type":"ChoiceOptionReference"},{"id":1,"name":"Highest","type":"ChoiceOptionReference"},{"id":2,"name":"High","type":"ChoiceOptionReference"},{"id":3,"name":"Normal","type":"ChoiceOptionReference"},{"id":4,"name":"Low","type":"ChoiceOptionReference"},{"id":5,"name":"Lowest","type":"ChoiceOptionReference"}],"sharedFields":[],"legacyRestName":"priority","trackerItemField":"priority","referenceType":"ChoiceOptionReference"},{"id":3,"name":"Summary","type":"TextField","hidden":False,"valueModel":"TextFieldValue","mandatoryInStatuses":[{"id":0,"name":"Unset","type":"ChoiceOptionReference"},{"id":1,"name":"New","type":"ChoiceOptionReference"},{"id":2,"name":"Verified","type":"ChoiceOptionReference"},{"id":3,"name":"Resolved","type":"ChoiceOptionReference"},{"id":4,"name":"Reopened","type":"ChoiceOptionReference"},{"id":5,"name":"Closed","type":"ChoiceOptionReference"}],"sharedFields":[],"legacyRestName":"name","trackerItemField":"name"},{"id":4,"name":"Submitted at","type":"DateField","hidden":False,"valueModel":"DateFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"submittedAt","trackerItemField":"createdAt"},{"id":5,"name":"Assigned to","type":"UserChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<UserReference>","mandatoryInStatuses":[],"multipleValues":True,"sharedFields":[],"legacyRestName":"assignedTo","trackerItemField":"assignedTo","referenceType":"UserReference"},{"id":6,"name":"Submitted by","type":"UserChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<UserReference>","mandatoryInStatuses":[],"multipleValues":False,"sharedFields":[],"legacyRestName":"submitter","trackerItemField":"createdBy","referenceType":"UserReference"},{"id":7,"name":"Status","type":"OptionChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<ChoiceOptionReference>","mandatoryInStatuses":[],"multipleValues":False,"options":[{"id":0,"name":"Unset","type":"ChoiceOptionReference"},{"id":1,"name":"New","type":"ChoiceOptionReference"},{"id":2,"name":"Verified","type":"ChoiceOptionReference"},{"id":3,"name":"Resolved","type":"ChoiceOptionReference"},{"id":4,"name":"Reopened","type":"ChoiceOptionReference"},{"id":5,"name":"Closed","type":"ChoiceOptionReference"}],"sharedFields":[],"legacyRestName":"status","trackerItemField":"status","referenceType":"ChoiceOptionReference"},{"id":8,"name":"Start Date","type":"DateField","hidden":False,"valueModel":"DateFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"startDate","trackerItemField":"startDate"},{"id":9,"name":"End Date","type":"DateField","hidden":False,"valueModel":"DateFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"endDate","trackerItemField":"endDate"},{"id":10,"name":"Planned Effort","type":"DurationField","hidden":False,"valueModel":"DurationFieldValue","title":"Planned<br>Effort","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"estimatedMillis","trackerItemField":"estimatedMillis"},{"id":11,"name":"Spent Effort","type":"DurationField","hidden":False,"valueModel":"DurationFieldValue","title":"Spent<br>Effort","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"spentMillis","trackerItemField":"spentMillis"},{"id":12,"name":"% Spent / Plan","type":"DecimalField","hidden":False,"valueModel":"DecimalFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"spentEstimatedHours"},{"id":13,"name":"Category","type":"OptionChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<ChoiceOptionReference>","mandatoryInStatuses":[],"multipleValues":False,"options":[],"sharedFields":[],"legacyRestName":"category","trackerItemField":"categories","referenceType":"ChoiceOptionReference"},{"id":14,"name":"Severity","type":"OptionChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<ChoiceOptionReference>","mandatoryInStatuses":[],"multipleValues":False,"options":[{"id":0,"name":"Unset","type":"ChoiceOptionReference"},{"id":1,"name":"Blocker","type":"ChoiceOptionReference"},{"id":2,"name":"Critical","type":"ChoiceOptionReference"},{"id":3,"name":"Minor","type":"ChoiceOptionReference"},{"id":4,"name":"Trivial","type":"ChoiceOptionReference"}],"sharedFields":[],"legacyRestName":"severity","trackerItemField":"severities","referenceType":"ChoiceOptionReference"},{"id":15,"name":"Resolution","type":"OptionChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<ChoiceOptionReference>","mandatoryInStatuses":[],"multipleValues":False,"options":[{"id":0,"name":"Unset","type":"ChoiceOptionReference"},{"id":1,"name":"Fixed","type":"ChoiceOptionReference"},{"id":2,"name":"Invalid","type":"ChoiceOptionReference"},{"id":3,"name":"Won't Fix","type":"ChoiceOptionReference"},{"id":4,"name":"Later","type":"ChoiceOptionReference"},{"id":5,"name":"Remind","type":"ChoiceOptionReference"},{"id":6,"name":"Duplicate","type":"ChoiceOptionReference"},{"id":7,"name":"Works for Me","type":"ChoiceOptionReference"},{"id":8,"name":"In Development","type":"ChoiceOptionReference"},{"id":9,"name":"Implemented","type":"ChoiceOptionReference"},{"id":10,"name":"Partly Implemented","type":"ChoiceOptionReference"}],"sharedFields":[],"legacyRestName":"resolution","trackerItemField":"resolutions","referenceType":"ChoiceOptionReference"},{"id":16,"name":"Platform","type":"TrackerItemChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<TrackerItemReference>","mandatoryInStatuses":[],"multipleValues":True,"sharedFields":[],"legacyRestName":"platform","trackerItemField":"platforms","referenceType":"TrackerItemReference"},{"id":17,"name":"Subject","type":"OptionChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<ChoiceOptionReference>","mandatoryInStatuses":[],"multipleValues":True,"options":[],"sharedFields":[],"legacyRestName":"subject","trackerItemField":"subjects","referenceType":"ChoiceOptionReference"},{"id":18,"name":"Accrued Effort","type":"DurationField","hidden":False,"valueModel":"DurationFieldValue","title":"Accrued<br>Effort","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"accruedMillis","trackerItemField":"accruedMillis"},{"id":19,"name":"Story Points","type":"IntegerField","hidden":False,"valueModel":"IntegerFieldValue","title":"Points","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"storyPoints","trackerItemField":"storyPoints"},{"id":29,"name":"Assigned at","type":"DateField","hidden":False,"valueModel":"DateFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"assignedAt","trackerItemField":"assignedAt"},{"id":31,"name":"Release","type":"TrackerItemChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<TrackerItemReference>","mandatoryInStatuses":[],"multipleValues":True,"sharedFields":[],"legacyRestName":"versions","trackerItemField":"versions","referenceType":"TrackerItemReference"},{"id":32,"name":"Owner","type":"UserChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<UserReference>","mandatoryInStatuses":[],"multipleValues":True,"sharedFields":[],"legacyRestName":"supervisors","trackerItemField":"owners","referenceType":"UserReference"},{"id":74,"name":"Modified at","type":"DateField","hidden":False,"valueModel":"DateFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"modifiedAt","trackerItemField":"modifiedAt"},{"id":75,"name":"Modified by","type":"UserChoiceField","hidden":False,"valueModel":"ChoiceFieldValue<UserReference>","mandatoryInStatuses":[],"multipleValues":False,"sharedFields":[],"legacyRestName":"modifier","trackerItemField":"modifiedBy","referenceType":"UserReference"},{"id":76,"name":"Parent","type":"ReferenceField","hidden":False,"valueModel":"NotSupportedFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"parent","trackerItemField":"parent"},{"id":79,"name":"Children","type":"ReferenceField","hidden":False,"valueModel":"NotSupportedFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"children","trackerItemField":"children"},{"id":80,"name":"Description","type":"WikiTextField","hidden":False,"valueModel":"WikiTextFieldValue","mandatoryInStatuses":[{"id":0,"name":"Unset","type":"ChoiceOptionReference"},{"id":1,"name":"New","type":"ChoiceOptionReference"},{"id":2,"name":"Verified","type":"ChoiceOptionReference"},{"id":3,"name":"Resolved","type":"ChoiceOptionReference"},{"id":4,"name":"Reopened","type":"ChoiceOptionReference"},{"id":5,"name":"Closed","type":"ChoiceOptionReference"}],"sharedFields":[],"legacyRestName":"description","trackerItemField":"description"},{"id":81,"name":"Closed at","type":"DateField","hidden":False,"valueModel":"DateFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"closedAt","trackerItemField":"closedAt"},{"id":84,"name":"Description Format","type":"TextField","hidden":False,"valueModel":"TextFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"descFormat","trackerItemField":"descriptionFormat"},{"id":85,"name":"Flags","type":"IntegerField","hidden":False,"valueModel":"IntegerFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"flags"},{"id":87,"name":"Revision","type":"IntegerField","hidden":False,"valueModel":"IntegerFieldValue","title":"Rev.","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"version","trackerItemField":"version"},{"id":88,"name":"Attachments","type":"ReferenceField","hidden":False,"valueModel":"NotSupportedFieldValue","mandatoryInStatuses":[],"sharedFields":[],"legacyRestName":"comments","trackerItemField":"comments"}]
    return jsonify(rawJson)


@tracker_bp.route('/<int:id>/fields', methods=['GET'])
@validate_authorization
def fields(id):
    fields = Field.query.filter_by(trackerId=id).all()
    return jsonify([{
        "id": field.id,
        "name": field.name,
        "type": field.type,
        "trackerId": id
    } for field in fields])
    
@tracker_bp.route('/<int:id>/fields/<int:field_id>', methods=['GET'])
@validate_authorization
def field(id, field_id):
    tracker = Tracker.query.get_or_404(id)
    field = Field.query.filter_by(id=field_id, trackerId=tracker.id).first() 


    if not field:
        return jsonify({'error': 'field not found'}), 404
    return jsonify({
        "id": field.id,
        "name": field.name,
        "type": field.type,
    })

@tracker_bp.route('/<int:id>/items', methods=['POST'])
@validate_authorization
def create_item(id):
    tracker = Tracker.query.get_or_404(id)
    status = Status.query.filter_by(id=51).first()
    status_value = CodebeamerEntityReference.query.filter_by(id=51).first()

    payload = request.get_json()
    name = payload.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400


    description = payload.get('description')

    item = Item(name=name, description=description, descriptionFormat="Wiki", tracker_id=tracker.id, status_id=status.id)
    db.session.add(item)
    db.session.commit()

    summary_field = Field(name="Summary", type="TextFieldValue", trackerId=id, itemId=item.id)
    db.session.add(summary_field)
    description_field = Field(name="Description", type="TextFieldValue", trackerId=id, itemId=item.id)
    db.session.add(description_field)
    assignedto_field = Field(name="Assigned To", type="UserReference", trackerId=id, itemId=item.id, values=[user_value])
    db.session.add(assignedto_field)
    status_field = Field(name="Status", type="ChoiceOptionReference", trackerId=id, itemId=item.id, values=[status_value])
    db.session.add(status_field)


    return jsonify({
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "descriptionFormat": item.descriptionFormat,
        "assignedTo": [{"id": user.id, "name": user.name, "email": user.email} for user in item.assignedTo],
        "tracker" : {"id": item.tracker.id, "name": item.tracker.name},
        "customFields": [{"type": customField.type, "value": customField.value} for customField in item.customFields],
        "status": {"id": status.id, "name": status.name, "type": status.type},
        "storyPoints": item.storyPoints
    })