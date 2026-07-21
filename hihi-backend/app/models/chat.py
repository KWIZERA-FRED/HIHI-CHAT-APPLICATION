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

def is_participant(chat: dict, user_id: str) -> bool:
      """Authorization check — call before letting a user read/send in a chat."""
      return ObjectId(user_id) in chat["participants"]

def update_last_message(chat_id: str,message_preview: dict ) -> None:
      """
    Denormalized update, called right after a message is inserted.
    message_preview should be small: {content, sender_id, created_at}
    """
      mongo.db.chats.update_one(   
           {"_id": ObjectId(chat_id)},
           {
                "$set": {
                     "last_message": message_preview,
                     "updated_at": datetime.now(timezone.utc),
                }
           },
           )

def create_indexes() -> None:
     # Chat list: filter by participant, sort by recency — single index covers both.
     mongo.db.chats.create_index([("participants", 1),("updated_at", -1)])
      # Speeds up find_existing_direct_chat's $all/$size lookup.
     mongo.db.chats.create_index([("participants", 1), ("is_group", 1)])

