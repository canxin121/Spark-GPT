import json
from typing import Dict, Optional, Tuple
from bidict import bidict
import nonebot
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageEvent
from pathlib import Path
from pydantic import BaseModel, Extra
from ..common.config import spark_persistor
import json


class BotInfo(BaseModel):
    # 此处的truename用uuid4来随机生成
    at: str=""
    bard_session_id:str=""
    rc:str=""
    r:str=""
    source:str="bard"
    # 这里做owner主要是用来hash，以区分不同用户的可能重名的bot
    owner: Optional[str]

    def to_dict(self) -> dict:
        return self.dict()

    def __hash__(self):
        return hash((self.source, self.owner))

    @classmethod
    def from_dict(cls, data: dict) -> "BotInfo":
        return cls(**data)


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


class UserData(BaseModel):
    sender: Sender
    last_reply_message_id: int = 0
    is_waiting: bool = False
    botinfo: Optional[BotInfo] 
    def __hash__(self):
        return hash((self.sender, self.last_reply_message_id))

    def to_dict(self) -> Dict:
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict) -> "UserData":
        return cls(**data)


# 储存Spark_Desk的临时数据
class BardTemper(BaseModel):
    # 储存以用户为主体的信息，用户的info和data，只会用到单项查找
    user_data_dict: dict[UserInfo, UserData] = {}
    # 储存以bot为主体的信息，所有bot的msgid，和对应的bot信息,用bidict来方便操作唯一的键值对
    msg_bot_bidict: bidict[int, BotInfo] = bidict()


def set_userdata(
    event: MessageEvent, user_data_dict: dict[UserInfo, UserData]
) -> Tuple[UserInfo, UserData]:
    """
    接受一个event和一个user_data_dict(全局的，所有用户的),在user_data_dict匹配(无则初次设置)用户的过往使用信息
    返回UserInfo和匹配后的(无则新建的)对应用户的current_user_dict结构为[UserInfo, UserData]
    """
    user_info = UserInfo(platform="qq", user_id=event.user_id)
    user_data = UserData(
        sender=Sender(
            user_id=event.user_id,
            user_name=event.sender.nickname or "<未知的的用户名>",
        )
    )
    return user_info, user_data_dict.setdefault(user_info, user_data)


def get_user_info_and_data(event: MessageEvent) -> Tuple[UserInfo, UserData]:
    """
    接受一个 event ，返回一个包含 UserInfo 和 UserData 的元组。
    仅仅将构造好的 UserInfo 和 UserData 构建成一个一个元组并返回。
    用来初次生成UserInfo和UserData
    """
    return (
        UserInfo(platform="qq", user_id=event.user_id),
        UserData(
            sender=Sender(
                user_id=event.user_id,
                user_name=event.sender.nickname or "<未知的的用户名>",
            )
        ),
    )


# 储存Bard的持久数据,提供一键保存和加载功能
class Bard_Persistor(BaseModel):
    path_: str = str(Path()) + "/data/spark_gpt/bard_data.json"
    pic_able: str = None
    url_able: str = "True"
    num_limit: int = 350
    mode: str = "black"
    cookie: str = ""
    proxy: str = ""
    superusers = []
    blacklist = []
    whitelist = []
    # user_dict: Dict[UserInfo, Dict["all" or "now", Dict[nickname, BotInfo]]] = {}
    user_dict: Dict[UserInfo, Dict[str, Dict[str, BotInfo]]] = {}
    auto_prompt: str = "默认"

    def __init__(self, **data):
        super().__init__(**data)
        
        get_config = nonebot.get_driver().config
        self.superusers = (
            get_config.bard_superusers
            if hasattr(get_config, "bard_superusers")
            else spark_persistor.superusers
        )
        self.blacklist = (
            get_config.bard_blacklist
            if hasattr(get_config, "bard_blacklist")
            else spark_persistor.blacklist
        )
        self.whitelist = (
            get_config.bard_whitelist
            if hasattr(get_config, "bard_whitelist")
            else spark_persistor.whitelist
        )
        self.mode = (
            get_config.bard_mode
            if hasattr(get_config, "bard_mode")
            and get_config.bard_mode in ["white", "black"]
            else spark_persistor.mode
        )
        self.pic_able = getattr(get_config, "bard_picable", spark_persistor.pic_able)
        self.url_able = getattr(get_config, "bard_urlable", spark_persistor.url_able)
        self.num_limit = int(
            getattr(get_config, "bard_limit", spark_persistor.num_limit)
        )
        self.cookie = getattr(get_config, "bard_cookie", self.cookie)


# 这里的配置即使在多平台，也应只初始化一次
bard_persistor = Bard_Persistor()
