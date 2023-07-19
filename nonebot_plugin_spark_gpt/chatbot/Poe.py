import asyncio
import uuid

from nonebot.log import logger
from nonebot.utils import run_sync

from .utils import poe
from ..common.config import config
from ..common.mytypes import CommonUserInfo, BotData, BotInfo
from ..common.user_data import common_users

COOKIE = ""
PROXY = ""
ABLE = True
SUBSCRIBE_ABLE = True
CLIENT = None
WHITE_LIST = ""


def load_config():
    global COOKIE, PROXY, ABLE, SUBSCRIBE_ABLE, WHITE_LIST
    ABLE = True
    SUBSCRIBE_ABLE = True
    try:
        PROXY = config.get_config(source="Poe配置", config_name="proxy")
    except Exception as e:
        logger.info(f"加载Poe配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")

    try:
        COOKIE = config.get_config(source="Poe配置", config_name="cookie")
    except Exception as e:
        ABLE = False
        SUBSCRIBE_ABLE = False
        logger.warning(f"加载Poe配置时warn:{str(e)},无法使用Poe")

    try:
        subscrid = config.get_config(source="Poe配置", config_name="cookie")
        if subscrid != "True":
            SUBSCRIBE_ABLE = False
            logger.warning(f"加载Poe配置时info:poe设定为未订阅,无法使用poe的订阅功能")
    except Exception as e:
        SUBSCRIBE_ABLE = False
        logger.warning(f"加载Poe配置时info:poe设定为未订阅,无法使用poe的订阅功能")
    try:
        WHITE_LIST = config.get_config(source="Poe配置", config_name="whitelist")
    except Exception as e:
        logger.warning(f"加载Poe配置时warn:{str(e)},订阅功能白名单用户无法正常获取")


load_config()


class Poe_Bot:
    def __init__(
            self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.lock = asyncio.Lock()
        self.nickname = bot_info.nickname
        self.common_userinfo = common_userinfo
        self.botdata = bot_data
        self.source = bot_data.source

        if self.source == "poe claude":
            self.base_model = "a2"
        elif self.source == "poe chatgpt":
            self.base_model = "chinchilla"
        elif self.source == "poe chatgpt4":
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
            self.base_model = "beaver"
        else:
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
            self.base_model = "a2_2"

        if not COOKIE:
            raise Exception("Poe的配置cookie没有填写,无法使用")

    def __hash__(self) -> int:
        return hash((self.common_userinfo.user_id, self.nickname))

    async def ask(self, question: str):
        if self.botdata.source == "poe chatgpt4" or self.botdata.source == "poe claude-2-100k":
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if not self.common_userinfo.user_id in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
        if self.botdata.prefix:
            question += self.botdata.prefix + "\n" + question
        if not self.botdata.handle:
            await self.refresh()
        try:
            answer = await self.chat(question)

            return answer
        except Exception as e:
            raise e

    async def refresh(self):
        if self.botdata.source == "poe chatgpt4" or self.botdata.source == "poe claude-2-100k":
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
        if not self.botdata.handle:
            try:
                await self.new_bot()
                await self.chat(self.botdata.prompt)
            except Exception as e:
                raise e
        else:
            try:
                await self.chat_break()
                await self.chat(self.botdata.prompt)
            except Exception as e:
                raise e

        return

    @run_sync
    def chat_break(self):
        detail_error = "未知错误"
        retry = 1
        if not CLIENT:
            try:
                self.new_client()
            except Exception as e:
                raise e
        while retry > 0:
            error = "未知错误"
            try:
                CLIENT.send_chat_break(self.botdata.handle)
                return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Poe在清除会话记录时error:{detail_error}")
                # # if retry % 1 == 0:
                #     try:
                #         self.new_client()
                #     except Exception as e:
                #         raise e
                retry -= 1
        error = f"Poe在清除会话记录时出错次数超过上限:{detail_error}"
        raise Exception(error)

    @run_sync
    def chat(self, question: str):
        if not CLIENT:
            try:
                self.new_client()
            except Exception as e:
                raise e
        retry = 1
        while retry > 0:
            detail_error = "未知错误"
            try:
                for chunk in CLIENT.send_message(self.botdata.handle, question):
                    pass
                return chunk["text"]
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Poe在询问时error:{str(detail_error)}")
                # if retry % 1 == 0:
                #     try:
                #         self.new_client()
                #     except Exception as e:
                #         raise e
                retry -= 1
        error = f"Poe在询问时错误次数超过上限:{detail_error}"
        logger.error(error)
        raise Exception(error)

    @run_sync
    def new_bot(self):
        if not CLIENT:
            try:
                self.new_client()
            except Exception as e:
                raise e
        generated_uuid = uuid.uuid4()
        random_handle = generated_uuid.hex.replace("-", "")[0:15]
        self.botdata.handle = random_handle
        retry = 1
        detail_error = "未知错误"
        while retry > 0:
            try:
                CLIENT.create_bot(
                    self.botdata.handle,
                    "在吗",
                    base_model=self.base_model,
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
        global CLIENT
        retry = 1
        detail_error = "未知错误"
        while retry > 0:
            try:
                if PROXY:
                    CLIENT = poe.Client(token=COOKIE, proxy=PROXY)
                    return
                else:
                    CLIENT = poe.Client(token=COOKIE)
                    return
            except Exception as e:
                detail_error = str(e)
                retry -= 1
                error = f"Poe在生成新的Client时报错:{detail_error}"
                logger.error(error)
        error = f"Poe在生成新的Client时报错次数超出上限:{detail_error}"
        logger.error(error)
        raise Exception(error)
