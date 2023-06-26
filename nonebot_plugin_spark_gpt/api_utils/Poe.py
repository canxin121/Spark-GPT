from typing import Dict, Literal
from nonebot.log import logger
from nonebot.utils import run_sync
from pydantic import BaseModel
from ..common.config import config
from EdgeGPT import Chatbot, ConversationStyle, ConversationStyle
from ..common.mytypes import CommonUserInfo, BotData, BotInfo
from ..common.user_data import common_users
import poe
import uuid


COOKIE = ""
PROXY = ""
ABLE = True


def load_config():
    global COOKIE, PROXY, ABLE
    ABLE = True
    try:
        PROXY = config.get_config(source="Poe配置", config_name="proxy")
    except Exception as e:
        logger.warning(f"加载Poe配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")

    try:
        COOKIE = config.get_config(source="Poe配置", config_name="cookie")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Poe配置时warn:{str(e)},无法使用Poe")


load_config()


class Poe_bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.is_waiting = False
        self.nickname = bot_info.nickname
        self.common_userinfo = common_userinfo
        self.botdata = bot_data
        self.client = None

        self.source = bot_data.source
        if self.source == "poe claude":
            self.base_model = "a2"
        else:
            self.base_model = "chinchilla"
        if not COOKIE:
            raise Exception("Poe的配置cookie没有填写,无法使用")

    def __hash__(self) -> int:
        return hash((self.common_userinfo.user_id, self.nickname))

    async def ask(self, question: str):
        self.is_waiting = True
        if not self.botdata.handle:
            try:
                await self.new_bot()
            except Exception as e:
                self.is_waiting = False
                raise e
        try:
            answer = await self.chat(question)
            self.is_waiting = False
            return answer
        except Exception as e:
            self.is_waiting = False
            raise e

    async def refresh(self):
        self.is_waiting = True
        if not self.botdata.handle:
            try:
                await self.new_bot()
            except Exception as e:
                self.is_waiting = False
                raise e
        else:
            try:
                await self.chat_break()
            except Exception as e:
                self.is_waiting = False
                raise e
        self.is_waiting = False
        return

    @run_sync
    def chat_break(self):
        detail_error = "未知错误"
        retry = 5
        if not self.client:
            try:
                self.new_client()
            except Exception as e:
                raise e
        while retry > 0:
            error = "未知错误"
            try:
                self.client.send_chat_break(self.botdata.handle)
                return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Poe在清除会话记录时error:{detail_error}")
                if retry % 3 == 0:
                    try:
                        self.new_client()
                    except Exception as e:
                        raise e
                retry -= 1
        error = f"Poe在清除会话记录时出错次数超过上限:{detail_error}"
        raise Exception(error)

    @run_sync
    def chat(self, question: str):
        if not self.client:
            try:
                self.new_client()
            except Exception as e:
                raise e
        retry = 5
        while retry > 0:
            detail_error = "未知错误"
            try:
                for chunk in self.client.send_message(self.botdata.handle, question):
                    pass
                return chunk["text"]
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Poe在询问时error:{str(detail_error)}")
                if retry % 3 == 0:
                    try:
                        self.new_client()
                    except Exception as e:
                        raise e
                retry -= 1
        error = f"Poe在询问时错误次数超过上限:{detail_error}"
        logger.error(error)
        raise Exception(error)

    @run_sync
    def new_bot(self):
        if len(self.botdata.prompt) > 848:
            error = "Poe在创建新的bot时报错:预设过长,长度不得长于848字符,请修改预设或删除bot后新建"
            logger.error(error)
            raise Exception(error)
        if not self.client:
            try:
                self.new_client()
            except Exception as e:
                raise e
        generated_uuid = uuid.uuid4()
        random_handle = generated_uuid.hex.replace("-", "")[0:15]
        self.botdata.handle = random_handle
        retry = 2
        detail_error = "未知错误"
        while retry > 0:
            try:
                self.client.create_bot(
                    self.botdata.handle, self.botdata.prompt, base_model=self.base_model
                )
                common_users.save_userdata(common_userinfo=self.common_userinfo)
                return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Poe在创建新的bot时报错:{detail_error}")
                if retry == 1:
                    try:
                        self.new_client()
                    except Exception as e:
                        raise e
                retry -= 1

        error = f"Poe在创建新的bot时报错次数超出上限:{detail_error}"
        logger.error(error)
        raise Exception(error)

    def new_client(self):
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                if PROXY:
                    self.client = poe.Client(token=COOKIE, proxy=PROXY)
                    return
                else:
                    self.client = poe.Client(token=COOKIE)
                    return
            except Exception as e:
                detail_error = str(e)
                retry -= 1
                error = f"Poe在生成新的Client时报错:{detail_error}"
                logger.error(error)
        error = f"Poe在生成新的Client时报错次数超出上限:{detail_error}"
        logger.error(error)
        raise Exception(error)
