import asyncio
from pymongo import MongoClient

USERNAME = "link-irc"
PASSWORD = "link123"

client = MongoClient(
    f"mongodb+srv://{USERNAME}:{PASSWORD}@maindb.ennpbrl.mongodb.net/?retryWrites=true&w=majority&appName=MainDB"
)
db = client["link_irc"]
sessions_db = db["sessions"]
# Keep track of the last known number of messages
last_message_count = 0


async def check_new_messages():
    global last_message_count

    while True:
        # Retrieve the current number of messages in the sessions collection
        current_message_count = sessions_db.count_documents({})

        # Compare with the last known count to detect new messages
        if current_message_count > last_message_count:
            print("New data detected!")  # Trigger your desired action here
            last_message_count = current_message_count

        # Sleep for a specified interval before checking again
        await asyncio.sleep(10)  # Adjust the interval (in seconds) as needed


# Start the background task to continuously check for new messages
async def start_background_tasks():
    asyncio.create_task(check_new_messages())


# Run the background task
asyncio.run(start_background_tasks())
