from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    keyName = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', foreign_keys=[project_id])

item_assigned_to_table = db.Table('item_assigned_to',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

item_custom_field_table = db.Table('item_custom_field',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('custom_field_type', db.String(255), db.ForeignKey('custom_field.type'), primary_key=True)
)

field_cer_table = db.Table('field_cer',
    db.Column('field_id', db.Integer, db.ForeignKey('field.id'), primary_key=True),
    db.Column('cer_id', db.Integer, db.ForeignKey('codebeamer_entity_reference.id'), primary_key=True)
)

item_cer_table = db.Table('item_cer',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('cer_id', db.Integer, db.ForeignKey('codebeamer_entity_reference.id'), primary_key=True)
)

item_owners_table = db.Table('item_owners',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

class CustomField(db.Model):
    type = db.Column(db.String(255), primary_key=True)
    value = db.Column(db.String(255), nullable=True)

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)

class Transition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    from_status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    to_status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    from_status = relationship('Status', foreign_keys=[from_status_id], backref='transitions_from')
    to_status = relationship('Status', foreign_keys=[to_status_id], backref='transitions_to')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    descriptionFormat = db.Column(db.String(255), nullable=True)
    assignedTo = db.relationship('User', secondary=item_assigned_to_table, backref='item_assignees')
    tracker_id = db.Column(db.Integer, db.ForeignKey('tracker.id'))
    tracker = db.relationship('Tracker', foreign_keys=[tracker_id])
    customFields = db.relationship('CustomField', secondary=item_custom_field_table, backref='items')
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=True)
    status = db.relationship('Status', foreign_keys=[status_id])
    storyPoints = db.Column(db.Integer, nullable=True)
    teams = db.relationship('CodebeamerEntityReference', secondary=item_cer_table, backref='items')
    owners = db.relationship('User', secondary=item_owners_table, backref='item_owners')

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    trackerId = db.Column(db.Integer, nullable=False)
    itemId = db.Column(db.Integer, nullable=True)
    values = db.relationship('CodebeamerEntityReference', secondary=field_cer_table, backref='fields')

   


# Relations & Associations
class CodebeamerEntityReference(db.Model):
    __tablename__ = 'codebeamer_entity_reference'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  
    type = db.Column(db.String(255), nullable=True)  
class Association(db.Model):
    __tablename__ = 'association'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    type_id = db.Column(db.Integer, db.ForeignKey('codebeamer_entity_reference.id'))
    from_id = db.Column(db.Integer, db.ForeignKey('codebeamer_entity_reference.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('codebeamer_entity_reference.id'))

    type = db.relationship('CodebeamerEntityReference', foreign_keys=[type_id])
    from_entity = db.relationship('CodebeamerEntityReference', foreign_keys=[from_id])
    to_entity = db.relationship('CodebeamerEntityReference', foreign_keys=[to_id])



    
