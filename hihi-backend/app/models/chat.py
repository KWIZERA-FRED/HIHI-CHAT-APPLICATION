from datetime import datetime, timezone
from bson import ObjectId
from app.extensions import mongo

def create_chat(participant_ids: list[str], is_group: bool = False, group_name: str | None =None) -> dict:
    now = datetime.now(timezone.utc)
    chat = {
        "participants": [ObjectId(pid) for pid in participant_ids],
        "is_group": is_group,
        "group_name": group_name,
        "last_message": None,
        "created_at": now,
        "updated_at": now,

    }
    result = mongo.db.chats.insert_one(chat)
    chat["_id"] = result.inserted_id
    return chat

def find_existing_direct_chat(user_a: str, user_b: str) -> dict | None:
     """Prevent duplicate 1:1 chats between the same two users."""
     return mongo.db.chats.find_one({
          "is_group": False,
          "participants": {
               "$all": [ObjectId(user_a), ObjectId(user_b)],
               "$size": 2,
          },
     })

def get_user_chats(user_id: str, limit: int = 30, before: datetime | None = None) -> list[dict]:
     """
    Chat list for the sidebar, most recently active first.
    Cursor-paginated on updated_at instead of skip() for performance at scale.
    """
     query = {"participants": ObjectId(user_id)}
     if before:
          query["updated_at"] = {"$lt": before}

     return list(
        mongo.db.chats.find(query)
        .sort("updated_at", -1)
        .limit(limit)
     )

def find_chat_by_id(chat_id: str) -> dict | None:
    return mongo.db.chats.find_one({"_id": ObjectId(chat_id)})  