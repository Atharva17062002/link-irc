import asyncio
import requests as http
import json

# Constants
BASE_URL = "https://e46e-103-183-44-61.ngrok-free.app"
LOGGED_IN_USER = None
LAST_MESSAGE = None


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
    username = input("Enter Username")
    password = input("Enter Password")

    try:
        response = http.post(
            f"{BASE_URL}/auth-user",
            json={"username": username, "password": password},
        )
        data = json.loads(response.json())
        LOGGED_IN_USER = data.get("_id", {}).get("$oid", None)
        print(f"Logged in as {LOGGED_IN_USER}")
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
        await get_all_messages(session_id)  # Go to send message
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
        await send_message(session_id)  # Go to send message
    except Exception as e:
        print(e)

async def get_all_messages(session_id):
    response = http.get(f"{BASE_URL}/get-all-messages/{session_id}")
    data = response.json()
    for message in data:
        content = message.get("content")
        userid = message.get("userid")
        print(f"{userid}: {content}")
    try:
        await send_message(session_id)
    except Exception as e:
        print(e)
    

async def send_message(session_id):
    while True:
        try:
            response = http.post(
                f"{BASE_URL}/send-message/{session_id}",
                json={"content": message, "userid": LOGGED_IN_USER},
            )
            print(f'{LOGGED_IN_USER} : {message}' )
        except Exception as e:
            print(e)


async def main():
    await main_menu()


if __name__ == "__main__":
    asyncio.run(main())