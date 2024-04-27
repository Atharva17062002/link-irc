from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os

USERNAME = os.getenv("mongo_username")
PASSWORD = os.getenv("mongo_password")


client = MongoClient(
    f"mongodb+srv://{USERNAME}:{PASSWORD}@maindb.ennpbrl.mongodb.net/?retryWrites=true&w=majority&appName=MainDB"
)
db = client["link_irc"]
collection = db["sessions"]


class Session(BaseModel):
    sessionid: int
    password: str
