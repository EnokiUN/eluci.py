import aiohttp
import asyncio
import os
import json
import typing
import aioconsole

REST_URL = os.getenv("REST_URL") or "https://eludris.tooty.xyz/"
GATEWAY_URL = os.getenv("GATEWAY_URL") or "wss://eludris.tooty.xyz/ws/"

class MessagePayload(typing.TypedDict):
    author: str
    content: str

class Message:
    __slots__ = ("author", "content")

    def __init__(self, data: MessagePayload):
        self.author = data["author"]
        self.content = data["content"]

async def gateway_hb(ws: aiohttp.ClientWebSocketResponse):
    while True:
        await ws.ping()
        await asyncio.sleep(15)

async def handle_input(session: aiohttp.ClientSession, name: str):
    while True:
        msg = await aioconsole.ainput()
        async with session.post(REST_URL, json={"author": name, "content": msg}) as resp:
            if not resp.status == 200:
                print("An unknown error with sending the message has occured", resp.status)

async def main(name: str):
    async with aiohttp.ClientSession() as session:
        ws = await session.ws_connect(GATEWAY_URL)
        asyncio.create_task(gateway_hb(ws))
        asyncio.create_task(handle_input(session, name))
        async for msg in ws:
            msg = Message(json.loads(msg.data))
            print(f"[{msg.author}]: {repr(msg.content)[1:-1]}")

if __name__ == "__main__":
    name = input("What's your name? > ")
    asyncio.run(main(name))
