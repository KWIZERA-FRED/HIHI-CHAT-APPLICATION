import jwt
import os
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import find_user_by_id

def generate_tokens(user_id: str) -> str: #generates a random token
    payload ={
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc)
    }

    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def decode_token(token: str) -> dict: #decodes the generated token for identity
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"],algorithms=["HS256"])

def token_required(f):
    """Decorator for routes that require a valid JWT in the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization","")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header.split(" ",1)[1]
        # split(" ", 1) → splits on the first space only, max 1 split
        # result: ["Bearer", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjV..."]
        # [1] grabs the second piece — the actual token

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        current_user = find_user_by_id(payload["user_id"])
        if not current_user:
            return jsonify({"error": "User not found"}), 401
        
        # Attach to request context so the route can use it
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated











