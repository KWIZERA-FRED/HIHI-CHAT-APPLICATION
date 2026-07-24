from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request

from app.models.chat import find_chat_by_id, is_participant, update_last_message
from app.models.message import (
    create_message,
    get_chat_messages,
    mark_messages_read,
    count_unread,
    to_public_dict,
)
from app.utils.auth import token_required
from app.extensions import socketio

message_bp = Blueprint("message", __name__, url_prefix="/api/chats/<chat_id>/messages")

def _get_authorised_chat(chat_id: str, user_id: str):
    """
    Shared guard used by every route below.
    Returns (chat, error_response). error_response is None if everything's fine.
    """
    if not ObjectId.is_valid(chat_id):
        return None, (jsonify({"error": "chat_id must be a valid ID"}), 400)

    chat = find_chat_by_id(chat_id)
    if not chat:
        return None, (jsonify({"error": "Chat not found"}), 404)
    if not is_participant(chat,user_id):
        return None, (jsonify({"error": "You are not a participant in this chat"}), 403)
    return chat, None

@message_bp.route("", methods=["POST"])
@token_required
def send_message(chat_id):
    """Send a message into a chat."""
    current_user_id = str(request.current_user["_id"])

    chat, error = _get_authorised_chat(chat_id,current_user_id)
    if error:
        return error

    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    message_type = (data.get("message_type") or "text").strip()

    if not content:
        return jsonify({"error": "content is required"}), 400
    if message_type not in ("text", "image", "file"):
        return jsonify({"error": "message_type must be text, image, or file"}), 400

    message = create_message(chat_id, current_user_id,content,message_type)

    update_last_message(chat_id,{
        "content":content,
        "sender_id": ObjectId(current_user_id),
        "created_at": message["created_at"]

    })

    # Broadcast to everyone currently in this chat room
    socketio.emit("new_message", to_public_dict(message), to=chat_id)


    return jsonify({"message": to_public_dict(message)}), 201

@message_bp.route("",methods=["GET"])
@token_required
def get_messages(chat_id):
    current_user_id = str(request.current_user["_id"])
    chat,error = _get_authorised_chat(chat_id,current_user_id)

    if error:
        return error

    try:
        limit = int(request.args.get("limit", 30))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    limit = max(1, min(limit, 100))
    before = None
    before_param = request.args.get("before")
    if before_param:
        try:
            before = datetime.fromisoformat(before_param)
        except ValueError:
            return jsonify({"error": "before must be a valid ISO timestamp"}), 400

    message = get_chat_messages(chat_id, limit = limit, before = before)

    return jsonify({"messages": [to_public_dict(msg) for msg in message]}),200

@message_bp.route("/read",methods=["POST"])
@token_required
def mark_read(chat_id):
     """Mark all unread messages in this chat as read by the current user."""
     current_user_id = str(request.current_user["_id"])
     chat,error = _get_authorised_chat(chat_id,current_user_id)

     if error:
             return error
     updated_count = mark_messages_read(chat_id,current_user_id)
     return jsonify({"marked_read": updated_count}), 200

@message_bp.route("/unread-count",methods=["GET"])
@token_required
def unread_count(chat_id):
     """Return how many unread messages the current user has in this chat."""
     current_user_id = str(request.current_user["_id"])
     chat,error = _get_authorised_chat(chat_id,current_user_id)

     if error:
             return error
     count = count_unread(chat_id,current_user_id)
     return jsonify({"unread_count": count}), 200






