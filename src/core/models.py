from pydantic import BaseModel
from pymongo import MongoClient
import os
from datetime import datetime

USERNAME = os.getenv("mongo_username")
PASSWORD = os.getenv("mongo_password")


client = MongoClient(
    f"mongodb+srv://manuloco:manuloco123@maindb.ennpbrl.mongodb.net/?retryWrites=true&w=majority&appName=MainDB"
)
db = client["link_irc"]
sessions_db = db["sessions"]
users_db = db["users"]
messages_db = db["messages"]

class Message(BaseModel):
    content: str
    userid: str
    createdat: datetime

class Session(BaseModel):
    sessionid: int
    adminid: str
    memberid: str
    messages: [Message]
    password: str

class User(BaseModel):
    username: str
    password: str


    