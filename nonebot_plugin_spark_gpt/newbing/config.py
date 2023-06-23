import json
from typing import Dict, List, Optional
import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent
from pathlib import Path
from pydantic import BaseModel, Extra
from EdgeGPT import Chatbot, ConversationStyle
from ..common.config import spark_persistor


class UserInfo(BaseModel):
    platform: str
    user_id: int

    def to_dict(self) -> dict:
        return self.dict()

    def __hash__(self):
        return hash((self.platform, self.user_id))

    @classmethod
    def from_dict(cls, data: dict) -> "UserInfo":
        return cls(**data)

    def to_string(self) -> str:
        return f"{self.platform}-{self.user_id}"

    @classmethod
    def from_string(cls, s: str) -> "UserInfo":
        platform, user_id = s.split("-")
        return cls(platform=platform, user_id=int(user_id))


class Sender(BaseModel, extra=Extra.ignore):
    user_id: int
    user_name: str

    def __hash__(self):
        return hash((self.user_id, self.user_name))

    def to_dict(self) -> Dict:
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict) -> "Sender":
        return cls(**data)


class UserData(BaseModel, arbitrary_types_allowed=True):
    sender: Sender
    chatbot: Optional[Chatbot] = None
    chatmode: str = "1"
    last_reply_message_id: str = 0
    last_suggests: list = []
    is_waiting: bool = False

    def __hash__(self):
        return hash((self.sender))

    def to_dict(self) -> Dict:
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict) -> "UserData":
        return cls(**data)


# 储存newbing的临时数据
class NewBingTemper(BaseModel):
    # 储存以用户为主体的信息，用户的info和data，只会用到单项查找
    user_data_dict: dict[UserInfo, UserData] = {}


def set_userdata(
    event: MessageEvent, user_data_dict: dict[UserInfo, UserData]
) -> UserData:
    """
    接受一个event和一个user_data_dict(全局的，所有用户的),在user_data_dict匹配(无则初次设置)用户的过往使用信息
    返回UserInfo和匹配后的(无则新建的)对应用户的current_user_dict结构为Dict[UserInfo, UserData]
    """
    user_info = UserInfo(platform="qq", user_id=event.user_id)
    user_data = UserData(
        sender=Sender(
            user_id=event.user_id,
            user_name=event.sender.nickname or "unknown",
        )
    )
    return user_info, user_data_dict.setdefault(user_info, user_data)


# 储存newbing的数据,不需要本地保存,每次启动从env读取覆盖即可
class NerBingPersistor(BaseModel):
    cookie_path_: str = str(Path()) + "/data/spark_gpt/newbing_cookie.json"
    cookies:List[dict] = []
    pic_able: str = None
    url_able: str = "True"
    suggest_able: str = "True"
    num_limit: int = 350
    proxy: str=""
    predownload : str = "True"
    forward : str = "True"
    blacklist: List[str] = []
    whitelist: List[str] = []
    wss_link:str = "wss://sydney.bing.com/sydney/ChatHub"
    mode: str = "black"

    def __init__(self, **data):
        super().__init__(**data)

        get_config = nonebot.get_driver().config

        self.blacklist = (
            get_config.newbing_blacklist
            if hasattr(get_config, "newbing_blacklist")
            else spark_persistor.blacklist
        )
        self.whitelist = (
            get_config.newbing_whitelist
            if hasattr(get_config, "newbing_whitelist")
            else spark_persistor.whitelist
        )
        self.mode = (
            get_config.newbing_mode
            if hasattr(get_config, "newbing_mode")
            and get_config.newbing_mode in ["white", "black"]
            else spark_persistor.mode
        )
        self.predownload = getattr(
            get_config, "newbing_predownload", self.predownload
        )
        self.forward = getattr(
            get_config, "newbing_forward", self.forward
        )
        self.proxy = getattr(get_config, "newbing_proxy", self.proxy)
        self.pic_able = getattr(get_config, "newbing_picable", spark_persistor.pic_able)
        self.url_able = getattr(get_config, "newbing_urlable", spark_persistor.url_able)
        self.wss_link = getattr(get_config, "newbing_wss_link", self.wss_link)
        self.suggest_able = getattr(
            get_config, "newbing_suggestable", spark_persistor.suggest_able
        )

        self.num_limit = int(
            getattr(get_config, "newbing_limit", spark_persistor.num_limit)
        )
        if not Path(self.cookie_path_).exists():
            Path(self.cookie_path_).touch(exist_ok=True)
        try:
            self.cookies = json.loads(open(self.cookie_path_, encoding="utf-8").read())
        except:
            self.cookies = []
# 这里的配置即使在多平台，也应只初始化一次
newbing_persistor = NerBingPersistor()
newbingtemper = NewBingTemper()