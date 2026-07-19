from datetime import datetime, timezone
from bson import ObjectId
from extensions import mongo, bycrpt

def create_user(username: str, email: str, password: str) -> dict:
      """Insert a new user and return the created document."""
      password_hash = bycrpt.generate_password_hash(password).decode("utf-8")
      user = {
            "username": username,
            "email": email.lower(),
            "avatar_url": None,
            "is_online": False,
            "last_seen": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
      }
      result = mongo.db.users.insert_one(user)
      user["_id"] = str(result.inserted_id)
      return user

def find_user_by_email(email: str) -> dict | None: 
      return mongo.db.users.find_one({"email": email.lower()})

def find_user_by_id(user_id: str) -> dict | None:
      return mongo.db.users.find_one({"_id": ObjectId(user_id)})

def find_users_by_ids(user_ids: list[str]) -> list[dict[str,any]]:
       """For 'start new chat' search. Requires the text index below."""
       object_ids = [ObjectId(uid) for uid in user_ids]
       return list(mongo.db.users.find(
             {
                   "_id": {"$in": object_ids},
                   "password_hash": 0 #never leak the hash
             }
       ))

def search_users(query: str, exclude_id: str, limit: int = 20) -> list[dict]:
       """For 'start new chat' search. Requires the text index below."""
       return list(mongo.db.find({
             "$text": {"$search": query},
             "_id": {"$ne": ObjectId(exclude_id)},
             },
             {"password_hash": 0}
             ).limit(mimit))

def check_password(user: dict, password: str) -> bool:
      return bycrpt.check_password_hash(user["password_hash"],password)

def set_online_status(user_id: str, is_online: bool) -> None:
      mongo.db.users.update_one(
            { "_id": ObjectId(user_id)},
            {"$set": {"is_online": is_online, "last_seen": datetime.now(timezone.utc)}}
            )
      
def to_public_dict(user: dict)-> dict:
          """Strip sensitive fields before sending a user doc to the client."""
          return{
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "avatar_url": user.get("avatar_url"),
                "is_online": user.get("is_online", False),
                "last_seen": user.get("last_seen").isoformat() if user.get("last_seen") else None,
    } 

def create_indexes() -> None:
       mongo.db.users.create_index("email", unique=True)
       mongo.db.users.create_index("username", unique=True)
       mongo.db.users.create_index([("username", "text")])


      


