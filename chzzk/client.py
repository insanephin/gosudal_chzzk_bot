import aiohttp, hashlib
from chzzk.api import apiClient
from chzzk.websocket import run
from chzzk.model import accountInterlock, accessToken, sessionCreate, accountInfo, sessionInfo, Message
from utils.logger import client_logger
from utils.db import load, save

class ChzzkClient:
    def __init__(self, clientId: str, clientSecret: str, redirectUri: str):
        self.state = f"pychzzk-{hashlib.md5(clientId.encode()).hexdigest()}"
        self.headers = {
            "Authorization": "Bearer",
            "Content-Type": "application/json"
        }

        self.clientId = clientId
        self.clientSecret = clientSecret
        self.redirectUri = redirectUri

        self.access_token: Optional[str] = None
        self.token_expiry: Optional[int] = None
        
        self.session = apiClient(base_url="https://openapi.chzzk.naver.com")


    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, token: str):
        self._access_token = token
        self.update_headers(token)


    def update_headers(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"

    async def get_access_token(self, code: str) -> accessToken:
        payload = {
            "grantType": "authorization_code",
            "clientId": self.clientId,
            "clientSecret": self.clientSecret,
            "code": code,
            "state": self.state,
        }
        result = await self.session.post("/auth/v1/token", json=payload)
        token = accessToken.parse_obj(result)
        self.access_token = token.accessToken
        self.token_expiry = token.expiresIn
        return token

    async def refresh_access_token(self, refresh_token: str) -> accessToken:
        payload = {
            "grantType": "refresh_token",
            "refreshToken": refresh_token,
            "clientId": self.clientId,
            "clientSecret": self.clientSecret,
        }
        result = await self.session.post("/auth/v1/token", json=payload)
        token = accessToken.parse_obj(result)
        self.access_token = token.accessToken
        self.token_expiry = token.expiresIn
        return token

    async def revoke_token(self):
        if not self.access_token:
            raise RuntimeError("Access token is not available.")
        payload = {
            "clientId": self.clientId,
            "clientSecret": self.clientSecret,
            "token": self.access_token,
            "tokenTypeHint": "access_token",
        }
        return await self.session.post("/auth/v1/token/revoke", json=payload)

    @staticmethod
    def check_auth(func):
        async def wrapper(self, *args, **kwargs):
            if not self.access_token:
                raise RuntimeError("Access token is not available. Please authenticate first.")
            return await func(self, *args, **kwargs)
        return wrapper

    @check_auth
    async def get_account_info(self):
        result = await self.session.get("/open/v1/users/me", headers=self.headers)
        return accountInfo.parse_obj(result)

    @check_auth
    async def get_session(self):
        result = await self.session.get("/open/v1/sessions", headers=self.headers)
        return [sessionInfo.parse_obj(session) for session in result.get('data', [])]

    @check_auth
    async def create_session(self):
        result = await self.session.get("/open/v1/sessions/auth", headers=self.headers)
        return sessionCreate.parse_obj(result)

    @check_auth
    async def subscribe_chat_event(self, sessionKey: str):
        params = {
            "sessionKey": sessionKey,
            "channelId": "1343a0e30ff0acb09f2477a698d070a4"
        }
        return await self.session.post("/open/v1/sessions/events/subscribe/chat", params=params, headers=self.headers)

    @check_auth
    async def unsubscribe_chat_event(self, sessionKey: str):
        params = {
            "sessionKey": sessionKey
        }
        return await self.session.post("/open/v1/sessions/events/unsubscribe/chat", params=params, headers=self.headers)

    @check_auth
    async def send_chat(self, message: str):
        if len(message) > 100:
            raise ValueError("Message length exceeds 100 characters.")

        payload = {
            "message": message
        }
        result = await self.session.post("/open/v1/chats/send", json=payload, headers=self.headers)
        return Message.parse_obj(result)

    @check_auth
    async def set_notice(self, message: str = None, channelId: str = None):
        if not message and not channelId:
            raise ValueError("Either message or channelId must be provided.")
        if message and len(message) > 100:
            raise ValueError("Message length exceeds 100 characters.")

        payload = {
            "message": message,
            "channelId": channelId
        }
        return await self.session.post("/open/v1/chats/notice", json=payload, headers=self.headers)

    async def connect_websocket(self):
        session_list = await self.get_session()
        saved_session = load("session.json")
        session_keys = [session.sessionKey for session in session_list]
        session_key = saved_session.get("sessionKey")
        url = saved_session.get("url")
        
        if (url and session_key) or (url and not session_key) or (session_key in session_keys):
            client_logger.info("Try to connect to websocket...")
            await run(url)
        elif not url or not session_key or not session_list:
            client_logger.info("No saved session found. Creating a new session...")
            new_session = await self.create_session()
            saved_session['url'] = new_session.url
            save("session.json", saved_session)
            
            client_logger.info(f"New session created: {new_session.url}")
            await run(new_session.url)

        return session_list