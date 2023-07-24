import asyncio
import uuid

from async_poe_client import Poe_Client
from nonebot.log import logger

from ..common.config import config
from ..common.mytypes import CommonUserInfo, BotData, BotInfo
from ..common.user_data import common_users

P_B = ""
FORMKEY = ""
PROXY = ""
ABLE = True
SUBSCRIBE_ABLE = True
SUGGEST_ABLE = True
CLIENT = None
WHITE_LIST = ""


def load_config():
    global P_B, FORMKEY, PROXY, ABLE, SUBSCRIBE_ABLE, WHITE_LIST, SUGGEST_ABLE
    ABLE = True
    SUBSCRIBE_ABLE = True
    try:
        PROXY = config.get_config(source="Poe配置", config_name="proxy")
    except Exception as e:
        logger.info(f"加载Poe配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")

    try:
        P_B = config.get_config(source="Poe配置", config_name="p_b")
    except Exception as e:
        ABLE = False
        SUBSCRIBE_ABLE = False
        logger.warning(f"加载Poe配置时warn:{str(e)},无法使用Poe")
    try:
        FORMKEY = config.get_config(source="Poe配置", config_name="formkey")
    except Exception as e:
        ABLE = False
        SUBSCRIBE_ABLE = False
        logger.warning(f"加载Poe配置时warn:{str(e)},无法使用Poe")
    try:
        arg = config.get_config(source="Poe配置", config_name="suggest_able")
        if arg == "True":
            SUGGEST_ABLE = True
        else:
            SUGGEST_ABLE = False
    except Exception as e:
        SUGGEST_ABLE = False
        logger.warning(f"加载Poe配置时warn:{str(e)},没有建议回复")
    try:
        subscribed = config.get_config(source="Poe配置", config_name="subscribed")
        if subscribed != "True":
            SUBSCRIBE_ABLE = False
            logger.warning("加载Poe配置时info:poe设定为未订阅,无法使用poe的订阅功能")
    except Exception:
        SUBSCRIBE_ABLE = False
        logger.warning("加载Poe配置时info:poe设定为未订阅,无法使用poe的订阅功能")
    try:
        WHITE_LIST += config.get_config(source="Poe配置", config_name="whitelist")
    except Exception as e:
        logger.warning(f"加载Poe配置时warn:{str(e)},订阅功能白名单用户无法正常获取")


load_config()


class Poe_Bot:
    def __init__(
            self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData,
    ):
        self.lock = asyncio.Lock()
        self.nickname = bot_info.nickname
        self.common_userinfo = common_userinfo
        self.botdata = bot_data
        self.source = bot_data.source

        if self.source == "poe claude":
            self.botdata.model = "a2"
        elif self.source == "poe chatgpt":
            self.botdata.model = "chinchilla"
        elif self.source == "poe chatgpt4":
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
            self.botdata.model = "beaver"
        else:
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
            self.botdata.model = "a2_2"
        common_users.save_userdata(self.common_userinfo)
        if not P_B and FORMKEY:
            raise Exception("Poe的配置cookie没有填写,无法使用")

    def __hash__(self) -> int:
        return hash((self.common_userinfo.user_id, self.nickname))

    async def ask(self, question: str):
        global CLIENT
        if CLIENT is None:
            CLIENT = await Poe_Client(P_B, FORMKEY, PROXY).create()
        if self.botdata.source == "poe chatgpt4" or self.botdata.source == "poe claude-2-100k":
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
        if question in ["1", "2", "3"] and (
                self.botdata.handle in CLIENT.bots.keys() and "Suggestion" in CLIENT.bots[self.botdata.handle] and
                CLIENT.bots[self.botdata.handle]["Suggestion"]):
            question = CLIENT.bots[self.botdata.handle]["Suggestion"][int(question) - 1]
        if self.botdata.prefix:
            question += self.botdata.prefix + "\n" + question
        if not self.botdata.handle:
            await self.refresh()
        try:
            answer = ''
            async for message in CLIENT.ask_stream(url_botname=self.botdata.handle, question=question,
                                                   suggest_able=True):
                answer += message
            return answer
        except Exception as e:
            logger.error(f"Poe询问时出错:{str(e)}")
            raise Exception(f"Poe询问时出错:{str(e)}")

    async def refresh(self):
        global CLIENT
        if CLIENT is None:
            CLIENT = await Poe_Client(P_B, FORMKEY, PROXY).create()
        if self.botdata.source == "poe chatgpt4" or self.botdata.source == "poe claude-2-100k":
            if not SUBSCRIBE_ABLE:
                raise Exception("Poe账户未订阅,无法使用订阅功能")
            if self.common_userinfo.user_id not in WHITE_LIST:
                raise Exception("你不在poe订阅功能白名单内,无法使用订阅功能")
        if not self.botdata.handle:
            try:
                generated_uuid = uuid.uuid4()
                self.botdata.handle = generated_uuid.hex.replace("-", "")[0:15]
                await CLIENT.create_bot(self.botdata.handle, "无", base_model=self.botdata.model,
                                        suggested_replies=SUGGEST_ABLE)
                if self.botdata.prompt:
                    await CLIENT.send_message(self.botdata.handle, self.botdata.prompt)
                common_users.save_userdata(self.common_userinfo)
            except Exception as e:
                logger.error(f"Poe刷新对话时出错:{str(e)}")
                raise Exception(f"Poe刷新对话时出错:{str(e)}")
        else:
            try:
                await CLIENT.send_chat_break(self.botdata.handle)
                if self.botdata.prompt:
                    await CLIENT.send_message(self.botdata.handle, self.botdata.prompt)
            except Exception as e:
                logger.error(f"Poe刷新对话时出错:{str(e)}")
                raise Exception(f"Poe刷新对话时出错:{str(e)}")
        return
