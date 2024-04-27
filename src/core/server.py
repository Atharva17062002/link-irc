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
    sessions_db.insert_one(session_dict)
    return json_util.dumps(session_dict)

@app.post('/send-message')
async def send_message(message: Message, session_id: str, password:str):
    message_dict = dict(message)
    # Find the session by session_id
    session = sessions_db.find_one({"sessionid": session_id,"password":password})
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Append the new message to the session's messages list
    if 'messages' in session:
        session['messages'].append(message_dict)
    else:
        session['messages'] = [message_dict]
    
    # Update the session document in the database
    sessions_db.update_one({"sessionid": session_id}, {"$set": {"messages": session['messages']}})
    
    return JSONResponse(content=message_dict, media_type="application/json")


@app.get('/get-all-messages')
async def get_all_messages(session_id: str, user_id: str, password:str):
    # Find the session by session_id
    session = sessions_db.find_one({"sessionid": session_id,"password": password})
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if user_id == session['adminid'] or user_id == session['memberid']:
        return JSONResponse(content=session['messages'], media_type="application/json")
    else:
        raise HTTPException(status_code=403, detail="User not authorized to view messages")


# @app.post("/auth-session")
# async def auth_session(session: Session):
#     session_dict = dict(session)
#     cursor = sessions_db.find_one(session_dict)
#     if cursor is None:
#         raise HTTPException(status_code=404, detail="Session not found")
#     return json_util.dumps(cursor)


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
