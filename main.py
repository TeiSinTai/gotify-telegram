from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramEntityTooLarge
from aiogram.client.session.aiohttp import AiohttpSession
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

socks5 = os.environ.get('SOCKS5', 'proxy_not_set')
if socks5 != 'proxy_not_set':
  session = AiohttpSession(proxy = socks5)
  telegram_bot = Bot(token=TELEGRAM_TOKEN, session=session)
else:
  telegram_bot = Bot(token=TELEGRAM_TOKEN)

errorCounter = 0
infinity = True

# define an exception handler
def exception_handler(loop, context):
  global infinity
  print("Global exception handler called: {}".format(context["message"]))
  infinity = False
  exit(1)

# Gotify Web Socket Methods
async def message_handler(websocket) -> None:
    async for message in websocket:
        global errorCounter
        logging.info(f"Message: {message}")
        message = json.loads(message)
        # -+=()._ are reserved symbols, TG require them to be backslash escaped
        # _ is used in italic formatting
        e_message = message["message"].translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "+":  r"\+",
                                          "_":  r"\_",
                                          "=":  r"\=",
                                          "(":  r"\(",
                                          ")":  r"\)",
                                          #"^":  r"\^",
                                          #"$":  r"\$",
                                          #"*":  r"\*",
                                          ".":  r"\.",
                                          "\\": r"\\"
                                          }))
        e_title = message["title"].translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "+":  r"\+",
                                          "_":  r"\_",
                                          "=":  r"\=",
                                          "(":  r"\(",
                                          ")":  r"\)",
                                          #"^":  r"\^",
                                          #"$":  r"\$",
                                          #"*":  r"\*",
                                          ".":  r"\.",
                                          "\\": r"\\"
                                          }))
        logging.info("Sending message: {} ".format(f'{message["title"]}: {message["message"][:50]}...'))
        success = False
        try:
          await telegram_bot.send_message(
            chat_id=CHAT_ID,
            text=f'{e_title}: {e_message}',
            parse_mode="MarkdownV2",
          )
          success = True
        except TelegramBadRequest as e:
          logging.info("Message malformed, details: {}".format(e))
        except TelegramEntityTooLarge:
          logging.info("Message too long, should truncate?..")
        except Exception as e:
          logging.info("Unknown exception: {}".format(e))
        if not success:
          logging.info("Fallback - sending HTML with truncate")
          try:
            await telegram_bot.send_message(
              chat_id=CHAT_ID,
              text=f'{message["title"]}: {message["message"][:4000]}',
              parse_mode="HTML",
            )
          except Exception as e:
            errorCounter = errorCounter + 1
            logging.info("Fallback N{} failed with exception: {}".format(errorCounter,e))
          if errorCounter > 5:
            raise ValueError("Too many errors!")


async def websocket_gotify(hostname: str, port: int, token: str) -> None:
    global infinity
    logging.info("Starting Gotify Websocket...")
    websocket_resource_url = f"ws://{hostname}:{port}/stream?token={token}"
    async with connect(uri=websocket_resource_url) as websocket:
        logging.info(
            "Connected to Gotify Websocket: {}:{}".format(GOTIFY_URL, GOTIFY_PORT)
        )
        failed = False
        try:
          await message_handler(websocket)
        except Exception as e:
          logging.info("Exception in WebSocket: {}".format(e))
          failed = True
          infinity = False
          exit(1)
        if failed:
          loop = asyncio.get_running_loop()
          logging.warning("Stopping the event loop from within worker_coroutine")
          print("Stopping the event loop from within worker_coroutine")
          loop.stop() # This stops the application

if __name__ == "__main__":
    loop = new_event_loop()
    set_event_loop(loop)
    loop.set_exception_handler(exception_handler)
    loop.create_task(
        websocket_gotify(hostname=GOTIFY_URL, port=GOTIFY_PORT, token=CLIENT_TOKEN)
    )
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Received exit, exiting")
        logging.info("Received exit, exiting")
    except Exception as e:
        print("Received exception, exiting to restart: {}".format(e))
        logging.info("Received exception, exiting to restart: {}".format(e))
    loop.run_until_complete(gather(Task.all_tasks()))
    loop.close()
