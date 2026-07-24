from bson import ObjectId
from flask import Blueprint, jsonify, request

from app.models.chat import (
    create_chat,
    find_existing_direct_chat,
    get_user_chats,
    to_public_dict,
)
from app.models.user import find_user_by_id
from app.utils.auth import token_required


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chats")


@chat_bp.route("", methods=["POST"])
@token_required
def start_direct_chat():
     """Create or return a direct chat with another registered user."""
     data = request.get_json(silent = True) or {}
     participant_id = (data.get("participant_id") or "").strip()
     current_user_id = str(request.current_user["_id"])

     if not participant_id:
          return jsonify({"error": "participant_id is required"}), 400

     if not ObjectId.is_valid(participant_id):
          return jsonify({"error": "participant_id must be a valid user ID"}), 400

     if participant_id == current_user_id:
          return jsonify({"error": "You cannot start a chat with yourself"}), 400

     if not find_user_by_id(participant_id):
          return jsonify({"error" : "Participant not found"}), 404

     
     existing_chat = find_existing_direct_chat(current_user_id, participant_id)

     if existing_chat:
          return jsonify({"chat": to_public_dict(existing_chat)})

     chat = create_chat([current_user_id,participant_id])
     return jsonify({"chat": to_public_dict(chat)}), 201  

@chat_bp.route("",methods=["GET"])
@token_required
def list_chats():
       """Return the authenticated user's chats, newest first."""
       try:
            limit = int(request.args.get("limit", 30))
       except ValueError:
            return jsonify({"error": "limit must be an integer"}),400

       limit = max(1, min(limit, 100))

       current_user_id = str(request.current_user["_id"])
       chats = get_user_chats(current_user_id,limit=limit)
       return jsonify({
             "chats": [to_public_dict(chat) for chat in chats]
        }),200

@chat_bp.route("/<chat_id>", methods=["GET"])
@token_required
def get_chat(chat_id):
     """Return a single chat by ID, if the current user is a participant."""
     from app.models.chat import find_chat_by_id, is_participant
     if not ObjectId.is_valid(chat_id):
           return jsonify({"error": "chat_id must be a valid ID"}), 400
     chat = find_chat_by_id(chat_id)
     if not chat:
          return jsonify({"error": "Chat not found"}), 404
     
     current_user_id = str(request.current_user["_id"]) 
     if not is_participant(chat,current_user_id):
          return jsonify({"error": "You are not a participant in this chat"}), 403

     return jsonify({"chat": to_public_dict(chat)}), 200



