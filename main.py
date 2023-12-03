from aiogram import Bot
import logging
from asyncio import set_event_loop, new_event_loop, gather, Task
from websockets import connect
import json
import os

GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_PORT = os.environ.get('GOTIFY_PORT')
APP_TOKEN = os.environ.get('GOTIFY_APP_TOKEN')
CLIENT_TOKEN = os.environ.get('GOTIFY_CLIENT_TOKEN')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

logging.basicConfig(level=logging.INFO)

telegram_bot = Bot(token=TELEGRAM_TOKEN)


# Gotify Web Socket Methods
async def message_handler(websocket) -> None:
    async for message in websocket:
        logging.info(f"Message: {message}")
        message = json.loads(message)
        logging.info("Sending message: {} ".format(message))
        await telegram_bot.send_message(
            chat_id=CHAT_ID,
            text=f'{message["title"]}: {message["message"]}',
            parse_mode="Markdown",
        )


async def websocket_gotify(hostname: str, port: int, token: str) -> None:
    logging.info("Starting Gotify Websocket...")
    websocket_resource_url = f"ws://{hostname}:{port}/stream?token={token}"
    async with connect(uri=websocket_resource_url) as websocket:
        logging.info(
            "Connected to Gotify Websocket: {}:{}".format(GOTIFY_URL, GOTIFY_PORT)
        )
        await message_handler(websocket)


if __name__ == "__main__":
    loop = new_event_loop()
    set_event_loop(loop)

    loop.create_task(
        websocket_gotify(hostname=GOTIFY_URL, port=GOTIFY_PORT, token=CLIENT_TOKEN)
    )
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Received exit, exiting")
    finally:
        pending_tasks = [
            task for task in Task.all_tasks() if not task.done()
        ]
        loop.run_until_complete(gather(*pending_tasks))
        loop.close()

