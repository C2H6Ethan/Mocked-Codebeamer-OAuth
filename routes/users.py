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

@user_bp.route('/search', methods=['POST'])
@validate_authorization
def search_users():
    payload = request.get_json()
    name = payload.get('name')
    
    if name is None:
        users = User.query.all()
    else: 
        users = User.query.filter_by(name=name).all()

        
    user_data = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        for user in users
    ]

    return_data = {
        "page": 1,
        "pageSize": 13,
        "total": len(user_data),
        "users": user_data
    }
    return jsonify(return_data)