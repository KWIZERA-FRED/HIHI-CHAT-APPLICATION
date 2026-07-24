import socketio
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# --- Step 1: log in as fred2 to get a JWT ---
resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "fred2@test.com",
    "password": "secret123"
})
fred_token = resp.json()["token"]
print("Fred logged in, token acquired.")

# --- Step 2: log in as amy to get a JWT ---
resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "amy@test.com",
    "password": "secret123"
})
amy_token = resp.json()["token"]
print("Amy logged in, token acquired.")

CHAT_ID = "6a61dfd773246fe50ee8b04c"  # the chat we've been testing with

# --- Step 3: connect two socket clients ---
fred_sio = socketio.Client()
amy_sio = socketio.Client()

@amy_sio.on("connected")
def amy_connected(data):
    print("Amy socket connected:", data)

@amy_sio.on("joined_chat")
def amy_joined(data):
    print("Amy joined chat:", data)

@amy_sio.on("new_message")
def amy_received(data):
    print("\n🔔 AMY RECEIVED LIVE MESSAGE:", data)

@fred_sio.on("connected")
def fred_connected(data):
    print("Fred socket connected:", data)

fred_sio.connect(BASE_URL, auth={"token": fred_token})
amy_sio.connect(BASE_URL, auth={"token": amy_token})

time.sleep(1)

# --- Step 4: Amy joins the chat room ---
amy_sio.emit("join_chat", {"chat_id": CHAT_ID})
time.sleep(1)

# --- Step 5: fred sends a message via the normal REST API ---
print("\nFred sending a message via REST...")
requests.post(
    f"{BASE_URL}/api/chats/{CHAT_ID}/messages",
    json={"content": "can you see this live?!"},
    headers={"Authorization": f"Bearer {fred_token}"}
)

# --- Step 6: wait to see if Amy's socket receives the broadcast ---
time.sleep(2)

fred_sio.disconnect()
amy_sio.disconnect()
print("\nDone.")