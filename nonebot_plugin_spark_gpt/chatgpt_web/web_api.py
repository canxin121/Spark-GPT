import json
from urllib.parse import urljoin
import httpx
from nonebot import logger
from .config import gptweb_persistor
from .chatgpt_web_func import random_uuid4

SESSION_TOKEN_KEY = "__Secure-next-auth.session-token"
CF_CLEARANCE_KEY = "cf_clearance"


class ChatGPT_web:
    def __init__(self) -> None:
        self.session_token = gptweb_persistor.session_token
        self.model = gptweb_persistor.model
        self.api_url = gptweb_persistor.api_url
        self.timeout = 30
        self.authorization = ""
        self.proxies = gptweb_persistor.proxy
        if self.session_token:
            self.auto_auth = False
        else:
            logger.warning("Chatgpt_web 未配置 session_token，无法使用")
        if self.api_url.startswith("https://chat.openai.com"):
            raise ValueError("无法使用官方API，请使用第三方API")

    async def gpt_web_chat(self, truename, parentname, text: str) -> str:
        if not self.authorization:
            await self.refresh_session()
            if not self.authorization:
                return "Token获取失败，请检查配置或API是否可用"
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            async with client.stream(
                "POST",
                urljoin(self.api_url, "backend-api/conversation"),
                headers={
                    "Accept": "text/event-stream",
                    "Authorization": f"Bearer {self.authorization}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
                    "X-Openai-Assistant-App-Id": "",
                    "Connection": "close",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://chat.openai.com/chat",
                },
                json={
                    "action": "next",
                    "messages": [
                        {
                            "id": random_uuid4(),
                            "author": {"role": "user"},
                            "role": "user",
                            "content": {"content_type": "text", "parts": [text]},
                        }
                    ],
                    "conversation_id": truename,
                    "parent_message_id": parentname,
                    "model": "",
                    "timezone_offset_min": -480,
                },
                timeout=self.timeout,
            ) as response:
                if response.status_code == 429:
                    msg = ""
                    _buffer = bytearray()
                    async for chunk in response.aiter_bytes():
                        _buffer.extend(chunk)
                    resp: dict = json.loads(_buffer.decode())
                    if detail := resp.get("detail"):
                        if isinstance(detail, str):
                            msg += "\n" + detail
                    return "请求过多，请放慢速度" + msg
                if response.status_code == 401:
                    return "token失效，请重新设置token"
                if response.status_code == 403:
                    return "API错误，请联系开发者修复"
                if response.status_code == 404:
                    return "会话不存在"
                if response.is_error:
                    _buffer = bytearray()
                    async for chunk in response.aiter_bytes():
                        _buffer.extend(chunk)
                    resp_text = _buffer.decode()
                    logger.warning(
                        f"非预期的响应内容: <r>HTTP{response.status_code}</r> {resp_text}"
                    )
                    return f"ChatGPT 服务器返回了非预期的内容: HTTP{response.status_code}\n{resp_text[:256]}"
                data_list = []
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = line[6:]
                        if data.startswith("{"):
                            try:
                                data_list.append(json.loads(data))
                            except Exception as e:
                                logger.warning(f"ChatGPT数据解析未知错误：{e}: {data}")
                if not data_list:
                    return "ChatGPT 服务器未返回任何内容"
                idx = -1
                while data_list[idx]["error"]:
                    idx -= 1
                answer_json = data_list[idx]
                answer_text = answer_json["message"]["content"]["parts"][0]
                parent_id = answer_json["message"]["id"]
                conversation_id = answer_json["conversation_id"]
                return answer_text, parent_id, conversation_id

    async def refresh_session(self) -> None:
        cookies = {
            SESSION_TOKEN_KEY: self.session_token,
        }
        async with httpx.AsyncClient(
            cookies=cookies,
            proxies=self.proxies,
            timeout=self.timeout,
        ) as client:
            response = await client.get(
                urljoin(self.api_url, "api/auth/session"),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
                },
            )
            try:
                self.session_token = (
                    response.cookies.get(SESSION_TOKEN_KEY) or self.session_token
                )
                self.authorization = response.json()["accessToken"]
            except Exception as e:
                logger.opt(colors=True, exception=e).error(
                    f"刷新会话失败: <r>HTTP{response.status_code}</r> {response.text}"
                )


gptweb_api = ChatGPT_web()
