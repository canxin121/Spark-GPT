import asyncio
import json
import uuid
from urllib.parse import urljoin

import httpx
from nonebot.log import logger

from ..common.config import config
from ..common.mytypes import BotData, BotInfo, CommonUserInfo
from ..common.user_data import common_users

SESSION_TOKEN_KEY = "__Secure-next-auth.session-token"
CF_CLEARANCE_KEY = "cf_clearance"
SESSION_TOKEN = ""
MODEL = ""
API_URL = ""
PROXIES = ""
ABLE = True


def load_config():
    global SESSION_TOKEN, SESSION_TOKEN_KEY, CF_CLEARANCE_KEY, MODEL, API_URL, PROXIES, ABLE
    ABLE = True
    try:
        SESSION_TOKEN = config.get_config("Chat GPT web配置", "session token")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载ChatGPT web的配置时warn:{str(e)},无法使用ChatGPTWeb")

    try:
        MODEL = config.get_config("Chat GPT web配置", "model")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载ChatGPT web的配置时warn:{str(e)},无法使用ChatGPTWeb")

    try:
        API_URL = config.get_config("Chat GPT web配置", "api_url")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载ChatGPT web的配置时warn:{str(e)},无法使用ChatGPTWeb")
    try:
        PROXIES = config.get_config("Chat GPT web配置", "proxy")
    except Exception as e:
        logger.info(f"加载ChatGPT web的配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")


load_config()


class ChatGPT_web_Bot:
    def __init__(
            self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.nickname = bot_info.nickname
        self.common_userinfo = common_userinfo
        self.botdata: BotData = bot_data
        self.timeout = 30
        self.authorization = ""
        self.lock = asyncio.Lock()
        if not (SESSION_TOKEN and MODEL and API_URL):
            raise Exception("ChatGPT web的必填配置session_token,model,api_url没有填写全,无法使用")
        if API_URL.startswith("https://chat.openai.com"):
            raise ValueError("无法使用官方API,请使用第三方api_url")

    def __hash__(self):
        return hash((self.nickname, self.common_userinfo.user_id))

    async def refresh(self):
        self.botdata.conversation_id = None
        self.botdata.parent_id = str(uuid.uuid4())
        if self.botdata.prompt:
            try:
                await self.send_query(self.botdata.prompt)
            except Exception as e:
                raise e

    async def ask(self, question: str):
        if not self.botdata.conversation_id:
            await self.refresh()
        if self.botdata.prefix:
            question = self.botdata.prefix + "\n" + question
        try:
            answer = await self.send_query(question=question)

            return answer
        except Exception as e:
            raise e

    async def send_query(self, question: str):
        if not self.authorization:
            await self.refresh_session()
            if not self.authorization:
                raise Exception("Token获取失败,请检查配置或API是否可用")
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                if PROXIES:
                    proxies = PROXIES
                else:
                    proxies = None
                async with httpx.AsyncClient(proxies=proxies) as client:
                    async with client.stream(
                            "POST",
                            urljoin(API_URL, "backend-api/conversation"),
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
                                        "id": str(uuid.uuid4()),
                                        "author": {"role": "user"},
                                        "role": "user",
                                        "content": {
                                            "content_type": "text",
                                            "parts": [question],
                                        },
                                    }
                                ],
                                "conversation_id": self.botdata.conversation_id,
                                "parent_message_id": self.botdata.parent_id,
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
                            raise Exception("请求过多,请放慢速度" + msg)
                        if response.status_code == 401:
                            raise Exception("token失效,请重新设置token")
                        if response.status_code == 403:
                            raise Exception("API错误,请联系开发者修复")
                        if response.status_code == 404:
                            await self.refresh()
                            raise Exception("会话不存在")
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
                            raise Exception("ChatGPT 服务器未返回任何内容")
                        idx = -1
                        while "error" not in data_list[idx].keys():
                            idx -= 1
                        answer_json = data_list[idx]
                        answer_text = answer_json["message"]["content"]["parts"][0]
                        self.botdata.parent_id = answer_json["message"]["id"]
                        self.botdata.conversation_id = answer_json["conversation_id"]
                        common_users.save_userdata(common_userinfo=self.common_userinfo)

                        return answer_text
            except Exception as e:
                detail_error = str(e) if str(e) else "未知错误"
                logger.error(f"ChatGPT web在发送请求时出错:{detail_error}")
                retry -= 1
        raise Exception(f"ChatGPT在发送请求时错误次数超过上限:{detail_error}")

    async def refresh_session(self) -> None:
        global SESSION_TOKEN
        cookies = {
            SESSION_TOKEN_KEY: SESSION_TOKEN,
        }
        if PROXIES:
            proxies = PROXIES
        else:
            proxies = None
        async with httpx.AsyncClient(
                cookies=cookies,
                proxies=proxies,
                timeout=self.timeout,
        ) as client:
            response = await client.get(
                urljoin(API_URL, "api/auth/session"),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
                },
            )
            try:
                SESSION_TOKEN = response.cookies.get(SESSION_TOKEN_KEY) or SESSION_TOKEN
                self.authorization = response.json()["accessToken"]
            except Exception as e:
                logger.opt(colors=True, exception=e).error(
                    f"刷新会话失败: <r>HTTP{response.status_code}</r> {response.text}"
                )
