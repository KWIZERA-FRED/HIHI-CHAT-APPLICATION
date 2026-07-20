from datetime import datetime, timezone
from bson import ObjectId
from app.extensions import mongo


def create_message(chat_id: str, sender_id: str, content: str, message_type: str = "text") -> dict:
    message = {
        "chat_id": ObjectId(chat_id),
        "sender_id": ObjectId(sender_id),
        "content": content,
        "message_type": message_type,
        "read_by": [ObjectId(sender_id)],  # sender has implicitly "read" their own message
        "created_at": datetime.now(timezone.utc),
    }
    result = mongo.db.messages.insert_one(message)
    message["_id"] = result.inserted_id
    return message


def get_chat_messages(chat_id: str, limit: int = 30, before: datetime | None = None) -> list[dict]:
    """
    Cursor-paginated message history — 'load older messages on scroll up'.
    before = created_at of the oldest message currently loaded on the client.
    """
    query = {"chat_id": ObjectId(chat_id)}
    if before:
        query["created_at"] = {"$lt": before}

    return list(
        mongo.db.messages.find(query)
        .sort("created_at", -1)
        .limit(limit)
    )

def mark_messages_read(chat_id: str, user_id: str) -> int:
    """Bulk mark-as-read for everything in a chat the user hasn't read yet."""
    result = mongo.db.messages.update_many(
        {
            "chat_id": ObjectId(chat_id),
            "read_by": {"$ne": ObjectId(user_id)},

        },
        {"$addToSet": {"read_by": ObjectId(user_id)}},
    )
    return result.modified_count
