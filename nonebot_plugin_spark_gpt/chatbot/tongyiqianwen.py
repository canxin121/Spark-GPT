import asyncio
import json
import random
import uuid

import aiohttp
from nonebot import logger

from ..common.config import config
from ..common.mytypes import CommonUserInfo, BotInfo, BotData
from ..common.user_data import common_users

XSRF_TOKEN = ""
COOKIE = ""
HEADER = {}
ABLE = False


def load_config():
    global XSRF_TOKEN, COOKIE, HEADER, ABLE, HEADER, COOKIE
    ABLE = True
    try:
        XSRF_TOKEN = config.get_config("通义千问配置", "XSRF_TOKEN")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载通义千问配置配置时warn: {str(e)},没有配置通义千问的xsrf_token,无法使用通义千问")
    try:
        COOKIE = config.get_config("通义千问配置", "cookie")
        HEADER = {
            "accept": "application/json,text/plain,*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json",
            "origin": "https://qianwen.aliyun.com",
            "referer": "https://qianwen.aliyun.com/chat",
            "sec-ch-ua": '\\"MicrosoftEdge\\";v=\\"111\\",\\"Not(A:Brand\\";v=\\"8\\",\\"Chromium\\";v=\\"111\\"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0(Macintosh;IntelMacOSX10_15_7)AppleWebKit/537.36(KHTML,likeGecko)Chrome/113.0.0.0Safari/537.36",
            "x-xsrf-token": XSRF_TOKEN,
            "cookie": COOKIE,
        }
        if ABLE:
            asyncio.run(heartbeat())
    except Exception as e:
        ABLE = False
        logger.warning(f"加载通义千问配置配置时warn: {str(e)},没有配置通义千问的cookie,无法使用通义千问")


async def heartbeat():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://qianwen.aliyun.com/heartbeat?type=1&", headers=HEADER
        ) as response:
            await asyncio.sleep(5)
            # logger.info("通义千问心跳:" + str(response.status))


load_config()


class TongYiQianWen_Bot:
    def __init__(
            self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.common_userinfo = common_userinfo
        self.lock = asyncio.Lock()
        self.botdata = bot_data

    def __hash__(self) -> int:
        return hash((self.common_userinfo, self.botdata.nickname))

    def generate_random_id(self):
        """模仿16进制生成随机数?"""
        random_str = ""
        for _ in range(32):
            random_str += random.choice("0123456789abcdef")
        return random_str

    async def ask(self, question: str):
        if not self.botdata.sessionId:
            await self.refresh()
        try:
            answer = await self._send_prompt(question)
            common_users.save_userdata(common_userinfo=self.common_userinfo)
            return answer
        except Exception as e:
            raise e

    async def refresh(self):
        try:
            await self.create_chat_context()
            common_users.save_userdata(common_userinfo=self.common_userinfo)
            return
        except Exception as e:
            raise e

    async def _send_prompt(self, question: str):
        global XSRF_TOKEN, COOKIE, HEADER
        headers = HEADER.copy()
        headers["accept"] = "text/event-stream"
        msgId = str(uuid.uuid4()).replace("-", "")

        # 创建消息体
        data = {
            "action": "next",
            "msgId": msgId,
            "parentMsgId": self.botdata.parentMsgId,
            "contents": [{"contentType": "text", "content": question}],
            "openSearch": True,
            "sessionId": self.botdata.sessionId,
            "model": "",
        }
        payload = json.dumps(data)
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            "https://qianwen.aliyun.com/conversation",
                            headers=headers,
                            data=payload,
                    ) as response:
                        async for line in response.content:
                            if line:
                                stripped_line = line.decode().replace("data:", "")
                                try:
                                    data = json.loads(stripped_line)
                                    if "errorMsg" in data.keys():
                                        raise Exception(data["errorMsg"])
                                    content = data["content"][0]
                                except json.decoder.JSONDecodeError as e:
                                    pass
                                except Exception as e:
                                    raise e
                        return content
            except Exception as e:
                detail_error = str(e)
                logger.error(f"通义千问在询问时error:{detail_error}")
                retry -= 1
        error = f"通义千问在询问时出错次数超过上限:{detail_error}"
        logger.error(error)
        raise Exception(error)

    async def create_chat_context(self):
        global XSRF_TOKEN, COOKIE, HEADER
        self.botdata.sessionId = "0"
        self.botdata.userId = ""
        self.botdata.parentMsgId = ""
        payload = {"firstQuery": "在吗"}
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            "https://qianwen.aliyun.com/addSession",
                            headers=HEADER,
                            json=payload,
                            raise_for_status=True,
                    ) as response:
                        data = await response.json()
                        if data.get("success"):
                            self.botdata.sessionId = data["data"].get("sessionId")
                            self.botdata.userId = data["data"].get("userId")
                            self.botdata.parentMsgId = "0"
                        return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"通义千问在刷新时error:{detail_error}")
                retry -= 1
        error = f"通义千问在刷新时出错次数超过上限:{detail_error}"
        logger.error(error)

        raise Exception(error)
