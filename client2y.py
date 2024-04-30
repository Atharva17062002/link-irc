import requests as http
import json
import threading, os
from time import sleep

BASE_URL = "http://127.0.0.1:8000"
LOGGED_IN_USER = None
USERNAME = None


def login():
    global LOGGED_IN_USER
    # username = input("Enter username: ")
    # password = input("Enter password: ")

    username = "manu"
    password = "1234"

    try:
        response = http.post(
            f"{BASE_URL}/auth-user",
            json={"username": username, "password": password},
        )
        return json.loads(response.json())

    except Exception as e:
        print(e)


USERNAME = login().get("username")
LOGGED_IN_USER = login().get("_id").get("$oid")
print(USERNAME)
print(LOGGED_IN_USER)


def session(session_id):
    threading.Thread(target=fetch_messages).start()

    while True:
        message = input("Enter message: ")
        try:
            response = http.post(
                f"{BASE_URL}/send-message/{session_id}",
                json={"content": message, "userid": str(USERNAME)},
            )
            print(response.json())
        except Exception as e:
            print(e)


def fetch_messages():
    while True:
        try:
            response = http.get(f"{BASE_URL}/get-last-messages/888")
            messages = response.json()
            # clear the screen
            print("\033[H\033[J")
            for message in messages:
                print(f"{message.get('userid', '')}> / {message.get('content', '')}")
            sleep(5)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    session(888)
