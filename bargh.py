from telethon import TelegramClient
import asyncio
import json
import random
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_username = "babolsartoday"
n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")

client = TelegramClient("anon", api_id, api_hash)

L = "لیست"
KH = "خاموشی"
JOME = "جمعه"
SHANBEH = "شنبه"


async def find_message():
    ids = []
    with open("id", "r") as mid:
        messageid = mid.read()
    async for message in client.iter_messages(channel_username, limit=20):
        if str(message.id) in messageid:
            break
        if L in str(message.text) and KH in str(message.text):
            ids.append(message.id)
    if ids:
        with open("id", "a") as mid:
            mid.write(f"{ids}\n")
    return ids


async def post_to(ids, tel_id, part_of_the_city, starter, ending):
    rooz = False
    final_text = ""
    if starter:
        final_text = f"{random.choice(starter)}\n"
    for i in ids:
        message = await client.get_messages(channel_username, ids=i)
        for part in message.message.split("\n"):
            if not rooz and (JOME in part or SHANBEH in part):
                for p in part.split():
                    if JOME in p or SHANBEH in p:
                        final_text += f"فردا {p}\n"
                        rooz = True
            if part.strip():
                if part_of_the_city in part:
                    final_text += f"{part.split()[0]} تا {part.split()[1]}\n"
    final_text += ending
    payload = {"message": final_text, "tel_id": tel_id}
    requests.post(n8n_webhook_url, json=payload)


async def main():
    with open("users.json", "r") as file:
        users = json.load(file)
    await client.start()
    ids = await find_message()
    ids = ids[::-1]
    if ids:
        for user in users:
            await post_to(
                ids,
                user["tel_id"],
                user["part_of_the_city"],
                user.get("starter", ""),
                user.get("ending", "برق میره"),
            )


asyncio.run(main())
