# client.py
import asyncio
import websockets

async def main():
    async with websockets.connect('ws://localhost:8000/ws') as websocket:
        while True:
            message = input("Enter message: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.run(main())

