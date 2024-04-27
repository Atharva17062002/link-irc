from fastapi import FastAPI, WebSocket
from bson import json_util
from fastapi import HTTPException
from utils import generate_client_id
from models import Session, collection

app = FastAPI()

clients = {}


# -----------test route---------------#
@app.get("/pymongo-test")
async def read_db():
    cursor = collection.find({})
    documents = list(cursor)
    return json_util.dumps(documents)


# -----------test route---------------#


@app.post("/create-session")
async def create_session(session: Session):
    session_dict = dict(session)
    # only create session if it does not exist
    cursor = collection.find_one(session_dict)
    if cursor is not None:
        raise HTTPException(status_code=400, detail="Session already exists")
    collection.insert_one(session_dict)
    return json_util.dumps(session_dict)


@app.post("/auth-session")
async def auth_session(session: Session):
    session_dict = dict(session)
    cursor = collection.find_one(session_dict)
    if cursor is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return json_util.dumps(cursor)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        client_id = generate_client_id()

        clients[client_id] = websocket
        print(f"Client with ID {client_id} connected")
        while True:
            data = await websocket.receive_text()
            response = f"Message text was: {data}"
            print(response)
            await websocket.send_text(response)

    except Exception as e:
        print(e)
        await websocket.close()
        print("Connection closed")
        del clients[client_id]
