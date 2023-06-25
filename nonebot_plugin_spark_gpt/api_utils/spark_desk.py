from nonebot.log import logger
import aiohttp
import base64
import copy
import json
from ..common.config import config
from ..common.user_data import common_users
from ..common.mytypes import BotData, BotInfo, CommonUserInfo

COOKIE = ""
FD = ""
GTTOKEN = ""
SID = ""
ABLE = True
HEADER = None


def load_config():
    global COOKIE, FD, GTTOKEN, SID, ABLE, HEADER,ABLE
    try:
        COOKIE = config.get_config("Spark Desk配置", "cookie")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Spark Desk配置时warn: {str(e)}")

    try:
        FD = config.get_config("Spark Desk配置", "fd")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Spark Desk配置时warn: {str(e)}")

    try:
        GTTOKEN = config.get_config("Spark Desk配置", "GtToken")
    except Exception as e:
        logger.warning(f"加载Spark Desk配置时warn: {str(e)}")

    try:
        SID = config.get_config("Spark Desk配置", "sid")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Spark Desk配置时warn: {str(e)}")
    HEADER = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": COOKIE,
        "Origin": "https://xinghuo.xfyun.cn",
        "Referer": "https://xinghuo.xfyun.cn/desk",
        "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }


load_config()


class SparkBot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.nickname = bot_info.nickname
        self.is_waiting = False
        self.common_userinfo = common_userinfo
        self.botdata = bot_data

    def __hash__(self) -> int:
        return hash(self.nickname)

    async def generate_chat_id(self):
        url = "https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/create-chat-list"
        payload = "{}"
        async with aiohttp.ClientSession(headers=HEADER) as session:
            retry_count = 0
            while retry_count < 3:
                try:
                    async with session.post(url, data=payload) as response:
                        response_data = await response.json()
                        if response_data["code"] == 0:
                            chat_list_id = response_data["data"]["id"]
                            return chat_list_id
                        else:
                            raise Exception(f"Error code: {response_data['code']}")
                except Exception as e:
                    logger.error(f"Spark Desk在生产Chatid时error:{str(e)}")
                    retry_count += 1
                    if retry_count >= 3:
                        raise e
            error = "Spark Desk在生产Chatid时出错次数超过上限"
            logger.error(error)
            raise Exception(error)

    # async def set_name(self, chat_id, question):
    #     url = "https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/rename-chat-list"
    #     question = question[:15]
    #     payload = {
    #         "chatListId": chat_id,
    #         "chatListName": question,
    #     }
    #     async with aiohttp.ClientSession(headers=HEADER) as session:
    #         retry_count = 0
    #         while retry_count < 3:
    #             try:
    #                 async with session.post(url, data=json.dumps(payload)) as response:
    #                     response_data = await response.json()
    #                     if response_data["code"] == 0:
    #                         return True
    #                     else:
    #                         raise Exception(
    #                             f"Failed to set chat name. Error code: {response_data['code']}"
    #                         )
    #             except Exception as e:
    #                 retry_count += 1
    #                 if retry_count >= 3:
    #                     raise Exception(f"Error setting chat name: {str(e)}.")

    def decode(self, text):
        try:
            decoded_data = base64.b64decode(text).decode("utf-8")
            return decoded_data
        except Exception as e:
            # logger.error("Spark_Desk 返回消息解码出错")
            return ""

    async def refresh(self):
        retry = 3
        self.is_waiting = True
        while retry > 0:
            try:
                self.botdata.chatid = await self.generate_chat_id()
                common_users.save_userdata(self.common_userinfo)
                self.is_waiting = False
                return
            except Exception as e:
                logger.error(f"SparkDesk刷新出错了:{str(e)}")
                retry -= 1
        self.is_waiting = False
        raise Exception("SparkDesk刷新时出错次数超过上限")

    async def ask(self, question):
        self.is_waiting = True
        if not self.botdata.chatid:
            try:
                await self.refresh()
                await self.ask_question(self.botdata.prompt)
            except Exception as e:
                self.is_waiting = False
                error = f"SparkDesk初始化时出错次数超过上限:{str(e)}"
                logger.error(error)
                raise Exception(error)
        try:
            answer = await self.ask_question(question=question)
        except Exception as e:
            self.is_waiting = False
            raise e
        self.is_waiting = False
        return answer

    async def ask_question(self, question):
        url = "https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat"
        payload = {
            "fd": FD,
            "chatId": self.botdata.chatid,
            "text": question,
            "GtToken": GTTOKEN,
            "sid": SID,
            "clientType": "1",
            "isBot": "0",
        }

        async with aiohttp.ClientSession(headers=HEADER) as session:
            retry_count = 3
            error = "未知错误"
            while retry_count > 0:
                try:
                    async with session.post(
                        url, data=payload, timeout=None
                    ) as response:
                        response_text = await response.text()
                        response_text = "".join(
                            self.decode(line[len("data:") :].rstrip().lstrip().encode())
                            for line in response_text.splitlines()
                            if line
                            and self.decode(
                                line[len("data:") :].rstrip().lstrip().encode()
                            )
                            != "zw"
                        ).replace("\n\n", "\n")
                        if response_text:
                            return response_text
                        else:
                            logger.error("Spark Desk没有返回值")
                            raise Exception("Spark Desk没有返回值")
                except Exception as e:
                    retry_count -= 1
                    error = str(e)
                    logger.error(f"SparkDesk询问时error:{error}")

            raise Exception(f"SparkDesk询问时出错次数超过上限")
