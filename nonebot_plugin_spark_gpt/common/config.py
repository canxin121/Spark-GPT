import json
from typing import Dict, List, Optional, Tuple
import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent
from pathlib import Path
from pydantic import BaseModel, Extra
import json


class BotInfo(BaseModel):
    # BotInfo本身储存就决定了它是单平台单来源的
    # 这里预留一些东西只是留作可能的修改使用
    nickname: Optional[str]
    truename: Optional[str]
    source: Optional[str]
    model: Optional[str]
    num_users: Optional[int]
    prompt_nickname: Optional[str]
    prompt: Optional[str]
    # 这里做owner主要是用来hash，以区分不同用户的可能重名的bot
    owner: Optional[str]
    last_suggests: Optional[List[str]] = []

    def to_dict(self) -> dict:
        return self.dict()

    def __hash__(self):
        return hash((self.nickname, self.truename, self.owner))

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
    wait_msg_id: Optional[int] = None
    last_reply_message_id: Dict[str, int] = {}
    is_waiting: bool = False

    def __hash__(self):
        return hash(
            (
                self.sender,
                self.wait_msg_id,
                self.last_reply_message_id,
                self.last_reply_message_id,
            )
        )

    def to_dict(self) -> Dict:
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict) -> "UserData":
        return cls(**data)


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


def set_userdata(
    event: MessageEvent, user_data_dict: dict[UserInfo, UserData]
) -> UserData:
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


# 储存spark的持久数据,提供一键保存和加载功能
class SparkPersistor(BaseModel):
    path_: str = str(Path()) + "/data/spark_gpt/spark_data.json"
    pic_able: str = None
    url_able: str = "True"
    suggest_able: str = "True"
    num_limit: int = 350
    #0为http版，1为playwright版本
    poe_api_mode: int = 1
    superusers: List[str] = []
    blacklist: List[str] = []
    whitelist: List[str] = []
    mode: str = "black"
    prompts_dict: Dict[str, str] = {
        "猫娘": "现在你将模仿一只猫娘，与我对话每一句话后面都要加上“喵”，如果你能明白我的意思，请回复“喵~你好主人”",
        "默认": "你是一个ai语言模型",
    }

    def __init__(self, **data):
        super().__init__(**data)
        try:
            saved_data = self.load()
            self.__dict__.update(saved_data)
        except:
            pass
        get_config = nonebot.get_driver().config
        self.superusers = (
            get_config.spark_superusers
            if hasattr(get_config, "spark_superusers")
            else self.superusers
        )
        self.blacklist = (
            get_config.spark_blacklist
            if hasattr(get_config, "spark_blacklist")
            else self.blacklist
        )
        self.whitelist = (
            get_config.spark_whitelist
            if hasattr(get_config, "spark_whitelist")
            else self.whitelist
        )
        self.mode = (
            get_config.spark_mode
            if hasattr(get_config, "spark_mode")
            and get_config.spark_mode in ["white", "black"]
            else self.mode
        )
        self.poe_api_mode = int(getattr(get_config, "poe_api_mode", 1))
        self.pic_able = getattr(get_config, "spark_picable", None)
        self.url_able = getattr(get_config, "spark_urlable", "True")
        self.suggest_able = getattr(get_config, "spark_suggestable", "True")
        self.num_limit = int(getattr(get_config, "spark_limit", 350))
        self.save()

    def save(self):
        Path(self.path_).parent.mkdir(parents=True, exist_ok=True)
        data = self.__dict__.copy()
        with open(self.path_, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load(self):
        with open(self.path_, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data


# 这里的配置即使在多平台，也应只初始化一次
spark_persistor = SparkPersistor()
