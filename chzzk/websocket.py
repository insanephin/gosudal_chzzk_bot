import socketio, json, asyncio
from chzzk.model import Chat
from utils.logger import ws_logger, command_logger
from utils.db import load, save

class sioClient(socketio.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_handlers = {}

    def command(self, name):
        def decorator(func):
            if name in self.command_handlers:
                raise ValueError(f"Command {name} already registered")
            self.command_handlers[name] = func
            return func
        return decorator

sio = sioClient(logger=False, reconnection=False)

@sio.event
async def connect():
    ws_logger.info("WebSocket connection established.")

@sio.event
async def disconnect():
    ws_logger.info("WebSocket connection closed or expired. Reset session.")
    save("session.json", {"sessionKey": "", "url": ""})
    await sio.disconnect()

@sio.event
async def connect_error(data):
    ws_logger.error(f"WebSocket connection error: {data}")


@sio.on("SYSTEM")
async def system_handler(data):
    message = await to_json(data)
    if not message:
        ws_logger.error("Received empty or invalid SYSTEM message.")
        return

    if message.get("type") == "connected":
        session_data = load("session.json")
        session_data["sessionKey"] = data.get("sessionKey", "")
        save("session.json", session_data)
        ws_logger.debug(f"Connected with sessionKey: {session_data['sessionKey']}")

        ws_logger.info("Subscribing to chat events...")
        await sio.client.subscribe_chat_event(session_data["sessionKey"])
    elif message.get("type") == "subscribed":
        ws_logger.debug(f"Subscribed: data={data}")
    elif message.get("type") == "unsubscribed":
        ws_logger.debug(f"Unsubscribed: data={data}")
    elif message.get("type") == "revoked":
        ws_logger.warning("Access token revoked. Please re-authenticate.")

@sio.on("CHAT")
async def chat_handler(data):
    chat = Chat.parse_obj(data)
    if not chat.content.startswith("!"):
        return

    split_content = chat.content.split(" ", 1)
    command_name = split_content[0].lstrip("!")
    if len(split_content) > 1:
        command_args = split_content[1]

    handler = sio.command_handlers.get(command_name)
    if not handler:
        ws_logger.warning(f"Unknown command: {command_name}")
        return

    try:
        if command_args:
            return await handler(chat, command_args)
        else:
            commands = load("commands.json")
            reply = commands.get(command_name)
            if not reply:
                ws_logger.warning(f"Command {command_name} not found in commands.json")
                return
            return await sio.client.send_chat_message(
                chat.channelId,
                reply
            )
    except Exception as e:
        ws_logger.error(f"Error handling command {command_name}", exc_info=True)

async def run(url: str):
    try:
        await sio.connect(url, transports=['websocket'])
        ws_logger.info(f"Connected to WebSocket at {url}")
        await sio.wait()
        if not sio.connected:
            ws_logger.error("WebSocket connection failed. Reconnecting...")
            await sio.client.connect_websocket()
    except socketio.exceptions.ConnectionError as e:
        ws_logger.error(f"Failed to connect to WebSocket: {e}")
    except Exception as e:
        ws_logger.error(f"An error occurred: {e}", exc_info=True)
