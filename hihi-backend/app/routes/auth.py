from flask import Blueprint, request, jsonify
from pymongo.errors import DuplicateKeyError
from app.models.user import create_user, find_user_by_email, to_public_dict, check_password
from app.utils.auth import generate_tokens, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    
    if find_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409
    
    try: 
        user = create_user(username, email, password)
    except DuplicateKeyError:
        # Race condition backstop — the unique index catches it even if the check above missed it
        return jsonify({"error": "Username or email already taken"}), 409
    
    token = generate_tokens(user["_id"])
    return jsonify({"token": token, "user": to_public_dict(user)}),201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    
    user = find_user_by_email(email)
    if not user or not check_password(user, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_tokens(user["_id"])
    return jsonify({"token": token, "user": to_public_dict(user)}), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    return jsonify({"user": to_public_dict(request.current_user)}), 200










