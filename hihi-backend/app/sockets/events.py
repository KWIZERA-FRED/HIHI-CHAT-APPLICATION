from flask import request
from flask_socketio import join_room, leave_room,emit,disconnect
from app.extensions import socketio
from app.utils.auth import decode_token
from app.models.user import find_user_by_id, set_online_status
from app.models.chat import find_chat_by_id, is_participant

# Maps a socket's connection id -> the authenticated user's id
# Lets us know who's on the other end of any given socket.
connected_users = {}

@socketio.on("connect")
def handle_connect(auth):
    """
    Runs when a client opens a socket connection.
    'auth' is a dict the client sends during connection, e.g. {"token": "..."}
    """
    token = (auth or {}).get("token") #get token from front-end connection string
    if not token:
        disconnect()
        return False
    try:
        payload = decode_token(token) #verify the token to identify the logged in user
    except Exception:
        disconnect()
        return False

    user = find_user_by_id(payload["user_id"]) #find verifie Id from token in Mongo DB
    if not user:
        disconnect()
        return 

    user_id = str(user["_id"])
    connected_users[request.sid] = user_id
    set_online_status(user_id, True)
    emit("connected",{"user_id":user_id}, to=request.sid)

@socketio.on("disconnect")
def handle_disconnect():
    """Runs when a client closes the connection (closes tab, loses network, etc.)."""
    user_id = connected_users.pop(request.sid, None)
    if user_id:
        set_online_status(user_id,False)

@socketio.on("join_chat")
def handle_join_chat(data):
     """Client asks to start listening for events in a specific chat."""
     print("DEBUG: join_chat received:", data)
     user_id = connected_users.get(request.sid)
     if not user_id:
         emit("error", {"error": "Not Authenticated"})
         return

     chat_id = (data or {}).get("chat_id")
     chat = find_chat_by_id(chat_id) if chat_id else None

     if not chat or not is_participant(chat, user_id):
         emit("error", {"error":"cannot join this chat"})
         return

     join_room(chat_id)
     print("DEBUG: joined room successfully:", chat_id)
     emit("joined_chat", {"chat_id": chat_id}, to=request.sid)

@socketio.on("leave_chat")
def handle_leave_chat(data):
    """Client stops listening for events in a chat (e.g. navigated away)."""
    chat_id = (data or {}).get("chat_id")
    if chat_id:
        leave_room(chat_id)





    


    



