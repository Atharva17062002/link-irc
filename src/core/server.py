from core import create_app
from bson import json_util, ObjectId
from fastapi import HTTPException, WebSocket
from fastapi.responses import JSONResponse

from core.utils import generate_client_id
from core.models import Session, User, sessions_db, users_db, messages_db, Message


app = create_app()
clients = {}


@app.post("/auth-user")
async def auth_user(user: User):
    user_dict = dict(user)
    cursor = users_db.find_one(user_dict)
    print(cursor)
    if cursor is None:
        raise HTTPException(status_code=404, detail="User not found")
    return json_util.dumps(cursor, default=json_util.default)


@app.post("/create-user")
async def create_user(user: User):
    user_dict = dict(user)
    cursor = users_db.find_one({"username": user_dict["username"]})
    if cursor is not None:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db.insert_one(user_dict)
    print(type(user_dict))
    return {"message": "User created successfully", "user": user_dict, "status": 200}


@app.post("/create-session")
async def create_session(session: Session):
    session_dict = dict(session)

    print(session_dict)
    # only create session if it does not exist
    cursor = sessions_db.find_one(session_dict)
    if cursor is not None:
        raise HTTPException(status_code=400, detail="Session already exists")

    sessions_db.insert_one(session_dict)
    return json_util.dumps(session_dict, default=json_util.default)


def get_session(session_id: int):
    session = sessions_db.find_one({"sessionid": session_id})
    if session:
        return Session(**session)
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/send-message/{session_id}")
async def send_message(session_id: int, message: Message):
    print(message)
    session = get_session(session_id)
    session.messages.append(message)
    # Save the updated session back to the database
    sessions_db.update_one({"sessionid": session_id}, {"$set": session.dict()})
    return {"message": "Message sent successfully"}


@app.get("/get-all-messages/{session_id}")
async def get_all_messages(session_id: int):
    session = get_session(session_id)
    return session.messages


@app.post("/auth-session/{session_id}/{user_id}")
async def auth_session(session_id: int, user_id: str):

    session = get_session(session_id)
    if session.memberid == user_id or session.adminid == user_id:
        return {"message": "User authenticated successfully"}
    else:
        raise HTTPException(status_code=401, detail="User not authenticated")


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
