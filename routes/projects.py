from flask import Blueprint, jsonify
from routes.authorization import validate_authorization
from models import Project, Tracker

project_bp = Blueprint('projects', __name__)

@project_bp.route('', methods=['GET'])
@validate_authorization
def projects():
    projects = Project.query.all()
    project_data = [
        {
            "id": project.id,
            "name": project.name,
        }
        for project in projects
    ]
    return jsonify(project_data), 200

@project_bp.route('/<int:id>/trackers', methods=['GET'])
@validate_authorization
def trackers(id):
    project = Project.query.get_or_404(id)
    trackers = Tracker.query.filter_by(project_id=project.id).all()

    # You can customize the data you want to return in the JSON response
    trackers_data = [
        {
            'id': tracker.id,
            'name': tracker.name,
        }
        for tracker in trackers
    ]

    return jsonify(trackers_data)

