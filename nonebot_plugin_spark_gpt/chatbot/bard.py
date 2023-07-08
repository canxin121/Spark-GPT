import asyncio
import httpx
from urllib.parse import quote
from nonebot.log import logger
import json
from nonebot.utils import run_sync
from ..common.config import config
from ..common.user_data import common_users
from ..common.mytypes import BotData, BotInfo, CommonUserInfo
from bardapi import Bard
import requests

PROXY = ""
ABLE = True
Secure1PSID = ""


def load_config():
    global Secure1PSID, PROXY, ABLE
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


load_config()

HEADER = {
    "Host": "bard.google.com",
    "X-Same-Domain": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "https://bard.google.com",
    "Referer": "https://bard.google.com/",
}


class Bard_Bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        global Secure1PSID
        self.lock = asyncio.Lock()
        self.common_userinfo = common_userinfo
        self.nickname = bot_info.nickname
        self.session = requests.Session()
        self.session.headers = HEADER
        self.bard_client = None
        if not Secure1PSID:
            raise Exception("Bard的配置Secure1PSID没有填写,无法使用")

    def __hash__(self) -> int:
        return hash((self.common_userinfo.user_id, self.nickname))

    async def refresh(self):
        global Secure1PSID
        self.session = None
        self.session = requests.Session()
        self.session.headers = HEADER
        self.session.cookies.set("__Secure-1PSID", Secure1PSID)
        try:
            await self.new_bard_client()
            return
        except Exception as e:
            raise e

    async def ask(self, question: str):
        global Secure1PSID
        if not "__Secure-1PSID" in self.session.cookies:
            try:
                await self.refresh()
            except Exception as e:
                raise e
        try:
            answer = await self.bard_talk(question)
            return answer
        except Exception as e:
            raise e

    @run_sync
    def new_bard_client(self):
        global Secure1PSID
        retry = 3
        while retry > 0:
            detail_error = "未知错误"
            try:
                if not PROXY:
                    self.bard_client = Bard(token=Secure1PSID, session=self.session)
                else:
                    self.bard_client = Bard(
                        token=Secure1PSID, session=self.session, proxies=PROXY
                    )
                return
            except Exception as e:
                detail_error = str(e)
                logger.error(f"bard在询问时报错:{detail_error}")
                retry -= 1
        error = f"bard在创建新bard_client时出错次数超过上限:{detail_error}"
        logger.error(error)
        raise Exception(error)

    @run_sync
    def bard_talk(self, question: str):
        global Secure1PSID
        retry = 3
        while retry > 0:
            detail_error = "未知错误"
            try:
                answer = self.bard_client.get_answer(question)["content"]
                return answer
            except Exception as e:
                retry -= 1
                detail_error = str(e)
                logger.error(f"bard在询问时error:{detail_error}")
        error = f"bard在询问时出错次数超过上限:{detail_error}"
        logger.error(error)
        raise Exception(error)
