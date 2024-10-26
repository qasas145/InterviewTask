from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import uuid

client = MongoClient("mongodb://mongodb:27017/")
db = client["TaskDatabase"]
users_collection = db["users"]
organizations_collection = db["organizations"]

api = Blueprint("api", __name__)

@api.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
    user = {
        "id": str(uuid.uuid4()),
        "name": data["name"],
        "email": data["email"],
        "password": hashed_password
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User created successfully"}), 201


@api.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    user = users_collection.find_one({"email": data["email"]})
    
    if user and check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(identity=data["email"])
        refresh_token = create_refresh_token(identity=data["email"])
        return jsonify({
            "message": "User authenticated",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    return jsonify({"message": "Invalid email or password"}), 401

@api.route("/refresh-token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({
        "message": "Token refreshed",
        "access_token": new_access_token
    })

@api.route("/organization", methods=["POST"])
@jwt_required()
def create_organization():
    data = request.get_json()
    organization = {
        "organization_id": str(uuid.uuid4()),
        "name": data["name"],
        "description": data["description"],
        "members": []
    }
    organizations_collection.insert_one(organization)
    return jsonify({"organization_id": organization["organization_id"]}), 201

@api.route("/organization/<organization_id>", methods=["GET"])
@jwt_required()
def get_organization(organization_id):
    organization = organizations_collection.find_one({"organization_id": organization_id})
    if not organization:
        return jsonify({"message": "Organization not found"}), 404
    
    return jsonify({
        "organization_id": organization["organization_id"],
        "name": organization["name"],
        "description": organization["description"],
        "organization_members": organization["members"]
    })

@api.route("/organization", methods=["GET"])
@jwt_required()
def get_all_organizations():
    organizations = organizations_collection.find()
    output = []
    for org in organizations:
        output.append({
            "organization_id": org["organization_id"],
            "name": org["name"],
            "description": org["description"],
            "organization_members": org["members"]
        })
    return jsonify(output)

@api.route("/organization/<organization_id>", methods=["PUT"])
@jwt_required()
def update_organization(organization_id):
    data = request.get_json()
    result = organizations_collection.update_one(
        {"organization_id": organization_id},
        {"$set": {"name": data["name"], "description": data["description"]}}
    )
    if result.matched_count == 0:
        return jsonify({"message": "Organization not found"}), 404
    return jsonify({
        "organization_id": organization_id,
        "name": data["name"],
        "description": data["description"]
    })

@api.route("/organization/<organization_id>", methods=["DELETE"])
@jwt_required()
def delete_organization(organization_id):
    result = organizations_collection.delete_one({"organization_id": organization_id})
    if result.deleted_count == 0:
        return jsonify({"message": "Organization not found"}), 404
    return jsonify({"message": "Organization deleted successfully"})

@api.route("/organization/<organization_id>/invite", methods=["POST"])
@jwt_required()
def invite_user(organization_id):
    data = request.get_json()
    organization = organizations_collection.find_one({"organization_id": organization_id})
    if not organization:
        return jsonify({"message": "Organization not found"}), 404
    
    new_member = {
        "name": data["user_email"],
        "email": data["user_email"],
        "access_level": "read-only"
    }
    organizations_collection.update_one(
        {"organization_id": organization_id},
        {"$push": {"members": new_member}}
    )
    return jsonify({"message": "User invited successfully"})
