import config, asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from chzzk.websocket import run
from utils.logger import server_logger
from utils.db import load, save

app = FastAPI()

async def fetch_auth_data(code: str):
    data = load("auth.json")
    token = await app.client.get_access_token(code)
    data['access_token'] = token.accessToken
    data['refresh_token'] = token.refreshToken
    save("auth.json", data)
    return True    

async def check_auth():
    auth_data = load("auth.json")
    if auth_data.get('access_token'):
        app.client.access_token = auth_data['access_token']
        me = await app.client.get_account_info()
        if me:
            server_logger.info(f"Authenticated as {me.channelName} (ID: {me.channelId})")
        else:
            await app.client.refresh_access_token(auth_data['refresh_token'])

    asyncio.create_task(app.client.connect_websocket())
    return
        
@app.on_event("startup")
async def startup_event():
    server_logger.info("Starting authentication process...")
    asyncio.create_task(check_auth())

@app.on_event("shutdown")
async def shutdown_event():
    await app.client.session.close()
    server_logger.info("Shutting down the client...")


@app.get("/", response_class=RedirectResponse)
async def root():
    redirect_url = f"https://chzzk.naver.com/account-interlock?clientId={config.clientId}&redirectUri={config.redirectUri}/callback&state={app.client.state}"
    return redirect_url

@app.get("/me")
async def get_me():
    try:
        me = await app.client.get_account_info()
        return {
            "channelId": me.channelId,
            "channelName": me.channelName
        }
    except Exception as e:
        server_logger.error(f"Error fetching account info: {e}")
        return {"error": "Failed to fetch account info. Please try again."}

@app.get("/callback")
async def callback(code: str, state: str):
    data = {"code": code, "state": state}
    try:
        save("auth.json", data)
    except ValueError as e:
        return {"error": str(e)}

    try:
        await fetch_auth_data(code)
    except Exception as e:
        server_logger.error(f"Error fetching access token: {e}")
        return {"error": "Failed to fetch access token. Please try again."}

    server_logger.info("Access token fetched successfully.")
    return {"status": "success"}
