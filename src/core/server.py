from core import create_app
from bson import json_util, ObjectId
from fastapi import HTTPException, WebSocket
from fastapi.responses import JSONResponse
from ddtrace import patch

from core.utils import generate_client_id, RedisManager
from core.models import Session, User, sessions_db, users_db, messages_db, Message

patch(fastapi=True)
app = create_app()
clients = {}


@app.post("/auth-user")
async def auth_user(user: User):
    user_dict = dict(user)
    cursor = users_db.find_one(user_dict)
    print(cursor)
    if cursor is None:
        raise HTTPException(status_code=404, detail="User not found")
    return json_util.dumps(cursor)


@app.post("/create-user")
async def create_user(user: User):
    user_dict = dict(user)
    cursor = users_db.find_one({"username": user_dict["username"]})
    if cursor is not None:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db.insert_one(user_dict)
    return JSONResponse(content=user_dict, media_type="application/json")


@app.post("/create-session")
async def create_session(session: Session):
    session_dict = dict(session)
    # only create session if it does not exist
    cursor = sessions_db.find_one(session_dict)
    if cursor is not None:
        raise HTTPException(status_code=400, detail="Session already exists")
    RedisManager.save("session", session.sessionid, json_util.dumps(session_dict))
    sessions_db.insert_one(session_dict)
    return json_util.dumps(session_dict)

def get_session(session_id: int):
    # Attempt to retrieve the session from Redis
    session_json = RedisManager.get("session", session_id)
    if session_json:
        # Session found in Redis, deserialize JSON and return as a Session instance
        return Session(**json_util.loads(session_json))
    else:
        # Session not found in Redis, fetch from the database
        session = sessions_db.find_one({"sessionid": session_id})
        if session:
            # Cache the session in Redis for future requests
            RedisManager.save("session", session_id, json_util.dumps(session))
            # Convert the retrieved session dictionary to a Session instance
            return Session(**session)
        else:
            raise HTTPException(status_code=404, detail="Session not found")



@app.post("/send-message/{session_id}")
async def send_message(session_id: int, message: Message):
    session = get_session(session_id)
    session.messages.append(message)
    # Save the updated session back to the database
    RedisManager.save("session", session_id, json_util.dumps(session.dict()))
    sessions_db.update_one({"sessionid": session_id}, {"$set": session.dict()})
    return {"message": "Message sent successfully"}



@app.get("/get-all-messages/{session_id}")
async def get_all_messages(session_id: int):
    session = get_session(session_id)
    return session.messages


@app.post("/auth-session")
async def auth_session(session: Session):
    session_dict = dict(session)
    # Attempt to retrieve the session from Redis
    session_json = RedisManager.get("session", session_dict["sessionid"])
    if session_json:
        # Session found in Redis, return it
        return json_util.loads(session_json)
    else:
        # Session not found in Redis, fetch from the database
        cursor = sessions_db.find_one(session_dict)
        if cursor:
            # Cache the session in Redis for future requests
            RedisManager.save("session", session_dict["sessionid"], json_util.dumps(cursor))
            return cursor
        else:
            raise HTTPException(status_code=404, detail="Session not found")



# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     try:
#         await websocket.accept()
#         client_id = generate_client_id()

#         clients[client_id] = websocket
#         print(f"Client with ID {client_id} connected")
#         while True:
#             data = await websocket.receive_text()
#             response = f"Message text was: {data}"
#             print(response)
#             await websocket.send_text(response)

#     except Exception as e:
#         print(e)
#         await websocket.close()
#         print("Connection closed")
#         del clients[client_id]
