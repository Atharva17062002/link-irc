import pymongo
import time


# Function to poll for new entries
def poll_for_new_entries(last_entry_id):
    while True:
        # Query for new entries
        new_entries = collection.find({"_id": {"$gt": last_entry_id}})
        for entry in new_entries:
            print("New entry found:", entry)
            # Update last_entry_id to the latest entry
            last_entry_id = entry["_id"]
        # Wait for some time before polling again
        time.sleep(5)  # You can adjust the polling interval as needed


# Get the ID of the last entry in the collection
last_entry = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
last_entry_id = last_entry["_id"] if last_entry else None

# Start polling
poll_for_new_entries(last_entry_id)
