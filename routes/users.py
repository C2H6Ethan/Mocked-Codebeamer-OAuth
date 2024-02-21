from flask import Blueprint, request, jsonify
from routes.authorization import validate_authorization
from models import Item, Tracker, Association, User, db, Field
import re

user_bp = Blueprint('users', __name__)

@user_bp.route('/findByName', methods=['GET'])
@validate_authorization
def find_user_by_name():
    name = request.args.get('name')
    user = User.query.filter_by(name=name).first()
    if user:
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email
        })
    else:
        return jsonify({
            "error": "User not found"
        }), 404