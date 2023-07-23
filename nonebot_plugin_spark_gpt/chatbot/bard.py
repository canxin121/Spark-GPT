import asyncio

from nonebot.log import logger

from .utils.Bard import AsyncChatbot
from ..common.config import config
from ..common.mytypes import BotData, BotInfo, CommonUserInfo

PROXY = ""
ABLE = True
Secure1PSID = ""
Secure1PSIDTS = ""


def load_config():
    global Secure1PSID, PROXY, ABLE, Secure1PSIDTS
    ABLE = True
    try:
        PROXY = config.get_config(source="Bard配置", config_name="proxy")
    except Exception as e:
        logger.info(f"加载Bard配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")

    try:
        Secure1PSID = config.get_config(source="Bard配置", config_name="__Secure-1PSID")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Bard配置时warn:{str(e)},无法使用Bard")
    try:
        Secure1PSIDTS = config.get_config(source="Bard配置", config_name="__Secure-1PSIDTS")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Bard配置时warn:{str(e)},无法使用Bard")


load_config()


class Bard_Bot:
    def __init__(
            self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        global Secure1PSID
        self.lock = asyncio.Lock()
        self.common_userinfo = common_userinfo
        self.nickname = bot_info.nickname
        self.chatbot = None
        if not Secure1PSID:
            raise Exception("Bard的配置Secure1PSID没有填写,无法使用")
        elif not Secure1PSIDTS:
            raise Exception("Bard的配置Secure1PSIDTS没有填写,无法使用")

    def __hash__(self) -> int:
        return hash((self.common_userinfo.user_id, self.nickname))

    async def refresh(self):
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                self.chatbot = await AsyncChatbot.create(Secure1PSID, Secure1PSIDTS)
                return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Bard在询问时error:{detail_error}")
                retry -= 1
        raise Exception(f"Bard在询问时报错次数超过上限:{detail_error}")

    async def ask(self, question: str):
        if not self.chatbot:
            await self.refresh()
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                answer = await self.chatbot.ask(question)
                return answer["content"]
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Bard在询问时error:{detail_error}")
                retry -= 1
        raise Exception(f"Bard在询问时报错次数超过上限:{detail_error}")
