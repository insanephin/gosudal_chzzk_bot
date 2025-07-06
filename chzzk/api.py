import aiohttp, hashlib
from typing import Optional
from aiohttp.client_exceptions import ClientError, ContentTypeError
from chzzk.model import accountInterlock, accessToken
from utils.logger import api_logger

class HTTPException(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"HTTP {code}: {message}")
        self.code = code
        self.message = message

class apiClient(aiohttp.ClientSession):
    def __init__(self, base_url: str, *args, **kwargs):
        self.base_url = base_url.rstrip("/")
        super().__init__(*args, **kwargs)

    async def _request_wrapper(self, method: str, endpoint: str, use_base=True, **kwargs):
        if use_base:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        else:
            url = endpoint

        try:
            async with super().request(method, url, **kwargs) as response:
                api_logger.debug(f"Request: {method} {url} | Params: {kwargs.get('params', {})} | Json: {kwargs.get('json', {})}")
                
                data = await response.json()
                code = data.get("code", response.status)
                api_logger.debug(f"Response: {code} | Data: {data}")

                if code == 200:
                    return data.get("content", {})
                elif 400 <= code <= 500:
                    raise HTTPException(code, data.get("message", "Client error"))
                else:
                    raise HTTPException(code, data.get("message", "Server error"))
        except ContentTypeError as e:
            return {"code": response.status, "message": "Invalid response format"}
        except ClientError as e:
            api_logger.error(f"HTTP request failed:", exc_info=True)
            raise HTTPException(500, str(e))

    async def get(self, endpoint: str, **kwargs) -> dict:
        return await self._request_wrapper("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> dict:
        return await self._request_wrapper("POST", endpoint, **kwargs)
