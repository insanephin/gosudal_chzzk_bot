import config, asyncio, logging, aiohttp, json
from chzzk.client import ChzzkClient
from chzzk.server import app
from chzzk.websocket import sio
from chzzk.model import Chat
from utils.logger import chat_logger

client = ChzzkClient(clientId=config.clientId, clientSecret=config.clientSecret, redirectUri=config.redirectUri+"/callback")
app.client = client
sio.client = client

@sio.command("멤버")
async def member(chat: Chat, command_args: str):
    commands["멤버"] = command_args
    save("commands.json", commands)
    
    ws_logger.info(f"Command 멤버 updated with args: {command_args}")
    command_logger.info(f"멤버 updated with args: {command_args} by {chat.profile.nickname} ({chat.senderChannelId})")
    await sio.client.send_chat_message(
        chat.channelId, 
        f"멤버 명령어가 업데이트되었습니다: {command_args}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8081)