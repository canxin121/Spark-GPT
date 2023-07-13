import asyncio
import uuid
import httpx
import json
import re
from nonebot.log import logger

from ..common.config import config
from ..common.mytypes import BotData, BotInfo, CommonUserInfo
from ..common.user_data import common_users


COOKIE = ""
PROXY = ""
ABLE = True
ORGANIZATION_UUID = ""


def load_config():
    global COOKIE, PROXY, ABLE
    ABLE = True
    try:
        COOKIE = config.get_config("Claude Ai配置", "cookie")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Claude Ai的配置时warn:{str(e)},无法使用Claude Ai")

    try:
        PROXY = config.get_config("Claude Ai配置", "proxy")
    except Exception as e:
        logger.info(f"加载Claude Ai配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")


load_config()


class Claude_Bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.lock = asyncio.Lock()
        self.botdata = bot_data
        self.common_userinfo = common_userinfo

    async def ask(self, question: str):
        if not ORGANIZATION_UUID:
            await self.get_organization_uuid()
        if not self.botdata.conversation_uuid:
            await self.refresh()
        if self.botdata.prefix:
            question = self.botdata.prefix + "\n" + question
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                result = ""
                async for msg in self.stream_msg(question):
                    result += msg
                return result
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Claude ai在询问时报错:{detail_error}")
                retry -= 1
        raise Exception(f"Claude ai在询问时报错次数超过上限:{detail_error}")

    async def refresh(self):
        if not ORGANIZATION_UUID:
            await self.get_organization_uuid()
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                await self.new_conversation_uuid()
                common_users.save_userdata(self.common_userinfo)
                if self.botdata.prompt:
                    retry = 3
                    detail_error = "未知错误"
                    while retry > 0:
                        try:
                            result = ""
                            async for msg in self.stream_msg(self.botdata.prompt):
                                result += msg
                            return result
                        except Exception as e:
                            detail_error = str(e)
                            logger.error(f"Claude ai在初始化预设时报错:{detail_error}")
                            retry -= 1
                    raise Exception(f"Claude ai在初始化预设时报错次数超过上限:{detail_error}")
                return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Claude ai在刷新时报错:{detail_error}")
        raise Exception(f"Claude ai在刷新时报错次数超过上限:{detail_error}")

    async def stream_msg(self, question: str):
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                "https://claude.ai/api/append_message",
                headers={
                    "Accept": "text/event-stream, text/event-stream",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "Content-Type": "application/json",
                    "Cookie": COOKIE,
                    "Origin": "https://claude.ai",
                    "Referer": f"https://claude.ai/chat/{self.botdata.conversation_uuid}",
                    "Sec-Ch-Ua": '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0",
                },
                json={
                    "completion": {
                        "prompt": question,
                        "timezone": "Asia/Shanghai",
                        "model": "claude-2",
                    },
                    "organization_uuid": ORGANIZATION_UUID,
                    "conversation_uuid": self.botdata.conversation_uuid,
                    "text": question,
                    "attachments": [],
                },
            ) as response:
                answer = ""
                async for chunk in response.aiter_text():
                    match = re.search(r'"completion":"(.*?)",', chunk)
                    if match:
                        new_answer = match.group(1)
                        add = new_answer[len(answer) :]
                        answer = new_answer
                        yield add

    async def get_organization_uuid(self):
        global ORGANIZATION_UUID
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://claude.ai/api/organizations",
                        headers={
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                            "Cache-Control": "max-age=0",
                            "Cookie": COOKIE,
                            "Sec-Ch-Ua": '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
                            "Sec-Ch-Ua-Mobile": "?0",
                            "Sec-Ch-Ua-Platform": '"Windows"',
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "navigate",
                            "Sec-Fetch-Site": "same-origin",
                            "Upgrade-Insecure-Requests": "1",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0",
                        },
                    )

                    raw_json = json.loads(response.text)
                    ORGANIZATION_UUID = raw_json[0]["uuid"]
                    return
            except Exception as e:
                retry -= 1
                detail_error = str(e)
                logger.error(f"Claude ai在获取organization_uuid时报错:{detail_error}")
        raise Exception(f"Claude ai在获取organization_uuid时报错次数超过上限:{detail_error}")

    async def new_conversation_uuid(self):
        new_uuid = str(uuid.uuid4())
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"https://claude.ai/api/organizations/{ORGANIZATION_UUID}/chat_conversations",
                json={"uuid": new_uuid, "name": ""},
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "Content-Type": "application/json",
                    "Origin": "https://claude.ai",
                    "Referer": "https://claude.ai/chats",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0",
                    "Cookie": COOKIE,
                },
            )
            print(response.status_code)
        self.botdata.conversation_uuid = new_uuid
        return
