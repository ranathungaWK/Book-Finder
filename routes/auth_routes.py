from flask import Blueprint, request, jsonify
from services.user_service import create_user, authenticate_user
from utils.validators import is_valid_email, is_strong_password , is_valid_username

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username" , "").strip()
    email = data.get("email" , "").strip()
    password = data.get("password" , "")

    if not username or not email or not password:
        return jsonify({"error":"All fields are required."}),400
    if not is_valid_username(username):
        return jsonify({"error":"Invalid username. Must be 3-30"}),400
    if not is_valid_email(email):
        return jsonify({"error":"Invalid email"}),400
    if not is_strong_password(password):
        return jsonify({"error":"Password must be at least 8 characters long."}),400

    user = create_user(username , email , password)

    if not user:
        return jsonify({"error":"User registration failed. Email may already be in use."}),400
    
    return jsonify({"message":"User registered successfully."}),201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email" , "").strip()
    password = data.get("password" , "")

    if not email or not password:
        return jsonify({"error":"Email and password are required."}),400
    
    user = authenticate_user(email , password)
    if not user:
        return jsonify({"error":"Invalid email or password."}),401
    
    return jsonify({"message":"Login successful."}),200