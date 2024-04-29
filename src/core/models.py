from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
import os
from datetime import datetime
from typing import List

USERNAME = os.getenv("mongo_username")
PASSWORD = os.getenv("mongo_password")


client = MongoClient(
    f"mongodb+srv://{USERNAME}:{PASSWORD}@maindb.ennpbrl.mongodb.net/?retryWrites=true&w=majority&appName=MainDB"
)
db = client["link_irc"]
sessions_db = db["sessions"]
users_db = db["users"]
messages_db = db["messages"]

class Message(BaseModel):
    content: str
    userid: str
    createdat: str

class Session(BaseModel):
    sessionid: int
    adminid: str
    memberid: str
    messages: List[Message] = []
    password: str
    created_by: Optional[str] = None

class User(BaseModel):
    username: str
    password: str


    