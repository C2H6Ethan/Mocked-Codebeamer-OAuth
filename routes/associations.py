from flask import Blueprint, request, jsonify
from routes.authorization import validate_authorization
from models import Association, CodebeamerEntityReference

association_bp = Blueprint('associations', __name__)

@association_bp.route('/<int:id>', methods=['GET'])
@validate_authorization
def association(id):
    association = Association.query.get_or_404(id)
    return jsonify({
        'id': association.id,
        'description': association.description,
        'from': {"id": association.from_entity.id, "name": association.from_entity.name},
        'to': {"id": association.to_entity.id, "name": association.to_entity.name},
        'type': {"id": association.type.id, "name": association.type.name},
    })