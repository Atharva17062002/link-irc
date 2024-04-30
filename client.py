import asyncio
import requests as http
import json
import threading, os
from time import sleep
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://foxhound-premium-antelope.ngrok-free.app"
LOGGED_IN_USER = None
USERNAME = None


async def main_menu():
    while True:
        print(">>>>>>>>>>>>>>Link IRC<<<<<<<<<<<<<<")
        print("1. Login")
        print("2. Register")
        choice = input("Enter your choice: ")
        if choice == "1":
            await login()
        elif choice == "2":
            await register()
        else:
            print("Invalid choice")


async def session_menu():
    while True:
        print("1. Create session")
        print("2. Join session")
        choice = input("Enter your choice: ")
        if choice == "1":
            await create_session()
        elif choice == "2":
            await join_session()
        else:
            print("Invalid choice")


async def register():
    username = input("Enter username: ")
    password = input("Enter password: ")
    try:
        response = http.post(
            f"{BASE_URL}/create-user",
            json={"username": username, "password": password},
        )
        print(response.json())
        await main_menu()  # Go back to main menu
    except Exception as e:
        print(e)


async def login():
    global LOGGED_IN_USER
    username = input("Enter username: ")
    password = input("Enter password: ")

    try:
        response = http.post(
            f"{BASE_URL}/auth-user",
            json={"username": username, "password": password},
        )
        data = json.loads(response.json())
        print(data)
        LOGGED_IN_USER = data.get("_id", {}).get("$oid", None)
        # print(f"Logged in as {LOGGED_IN_USER}")
        global USERNAME
        USERNAME = data.get("username", None)
        print(f"Logged in as {USERNAME} with id: {LOGGED_IN_USER}")
        await session_menu()  # Go to session menu
    except Exception as e:
        print(e)


async def join_session():
    if not LOGGED_IN_USER:
        print("You must log in first")
        return
    session_id = input("Enter session id: ")
    try:
        response = http.post(
            f"{BASE_URL}/auth-session/{session_id}/{LOGGED_IN_USER}",
            json={"userid": LOGGED_IN_USER},
        )
        print(response.json())
        await send_message(session_id)  # Go to send message
    except Exception as e:
        print(e)


async def create_session():
    if not LOGGED_IN_USER:
        print("You must log in first")
        return
    try:
        session_id = input("Enter session id: ")
        response = http.post(
            f"{BASE_URL}/create-session",
            json={
                "sessionid": session_id,
                "adminid": LOGGED_IN_USER,
                "memberid": LOGGED_IN_USER,
            },
        )

        data = json.loads(response.json())
        session_id = data.get("sessionid", None)
        print(f"Session created with id: {session_id}")
        # run the fetch_messages coroutine in the background
        asyncio.create_task(fetch_messages(session_id))
        await send_message(session_id)  # Go to send message

    except Exception as e:
        print(e)


async def send_message(session_id):
    threading.Thread(target=fetch_messages).start()

    while True:
        # Handle user input (send a new message)
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


async def main():
    await main_menu()


if __name__ == "__main__":
    threading.Thread(target=asyncio.run, args=(main(),)).start()
    # create a new thread to run fetch_messages
