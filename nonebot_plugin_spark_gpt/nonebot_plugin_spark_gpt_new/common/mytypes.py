import json
from pathlib import Path
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel
from EdgeGPT import Chatbot

PLATFORM = Literal["qq", "telegram"]
SOURCE = Literal[
    "poe chatgpt",
    "poe claude",
    "chatgpt web",
    "slack claude",
    "spark desk",
    "bing",
    "bard",
]


class BotInfo(BaseModel):
    """Bot的信息

    :param nickname: Bot的别名
    :type nickname: str
    """

    nickname: str

    def __hash__(self):
        return hash(self.nickname)

    def save(self) -> str:
        return f"{self.nickname}"

    @classmethod
    def load(cls, nickname: str) -> "BotInfo":
        return cls(nickname=nickname)


class BotData(BaseModel):
    """Bot的数据类型

    :param nickname: bot的别名
    :type nickname: str
    :param id: bot的id
    :type id: str
    :param owner: bot的拥有者
    :type owner: str
    :param is_waiting: bot是否正在等待
    :type is_waiting: bool
    :param last_suggests: bot的最后的建议回复
    :type last_suggests: List[str]
    :param source: bot的来源
    :type source: str
    :param model: bot的ai模型
    :type model: str
    :param num_users: bot的正在使用人数
    :type num_users: int
    :param prompt_nickname: bot的预设名
    :type prompt_nickname: str
    :param prompt: bot的预设内容
    :type prompt: str
    """

    nickname: Optional[str]
    handle: Optional[str]
    conversation_id: Optional[str]
    parent_id: Optional[str]
    msg_ts: Optional[str]
    thread_ts: Optional[str]
    session_id: Optional[str]
    bard_r: Optional[str]
    bard_rc: Optional[str]
    bard_at: Optional[str]
    id: Optional[str]
    owner: Optional[str]
    is_waiting: Optional[bool]
    last_suggests: Optional[List[str]] = []
    source: SOURCE
    model: Optional[str]
    num_users: Optional[int]
    prompt_nickname: Optional[str]
    prompt: Optional[str]
    chatid: Optional[str]

    def __hash__(self):
        return hash((self.nickname, self.owner))

    def save(self) -> dict:
        """
        将对象转换为字典

        :return: 转换后的字典
        :rtype: dict
        """
        return self.dict()

    @classmethod
    def load(cls, data: dict) -> "BotInfo":
        """
        根据字典创建对象

        :param data: 字典数据
        :type data: dict
        :return: 创建的对象
        :rtype: BotInfo
        """
        return cls(**data)


class UserInfo(BaseModel):
    """用户的平台信息类型

    :param platform: 用户所在平台
    :type platform: PLATFORM
    :param username: 用户名(必须在本平台唯一)
    :type username: str
    """

    platform: PLATFORM
    username: str

    def to_dict(self) -> dict:
        return self.dict()

    def __hash__(self):
        return hash((self.platform, self.username))

    def save(self) -> str:
        return f"{self.platform}-{self.username}"

    @classmethod
    def load(cls, userinfo: str) -> "UserInfo":
        platform, username = userinfo.split("-")
        return cls(platform=platform, username=str(username))


class CommonUserData(BaseModel):
    """用户数据

    :param bots: 用户的所有bots
    :type bots: Dict[BotInfo, BotData]
    :param key: 用户的验证密钥
    :type key: str
    """

    bots: Dict[BotInfo, BotData]
    user_id: str
    key: str

    def __hash__(self):
        return hash(())

    def save(self) -> Dict:
        data = {
            "bots": {},
            "user_id": self.user_id,
            "key": self.key,
        }
        for botinfo, botdata in self.bots.items():
            data["bots"][botinfo.save()] = botdata.save()
        path: Path = Path() / f"data/spark_gpt/common/common_users/{self.user_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        with open(path, "w") as f:
            json.dump(data, f)
        return data

    @classmethod
    def load(cls, data: Dict) -> "CommonUserData":
        newdata = {"bots": {}, "user_id": data["user_id"], "key": data["key"]}
        for botinfo, botdata in data["bots"].items():
            newdata["bots"][BotInfo.load(botinfo)] = BotData.load(botdata)
        return cls(**newdata)


class CommonUserInfo(BaseModel):
    """用户通用身份

    :param user_id: 用户的唯一特征id
    :type user_id: str
    """

    user_id: str

    def __hash__(self):
        return hash(self.user_id)

    def save(self) -> str:
        return self.user_id

    @classmethod
    def load(cls, user_id: str) -> "CommonUserInfo":
        return cls(user_id=user_id)


class UsersInfo(BaseModel):
    users: List[UserInfo]

    def __hash__(self):
        # 将所有用户信息的哈希值相加得到 Usersinfo 的哈希值
        return sum(hash(user) for user in self.users)
    
    def save(self) -> list:
        data = [user.save() for user in self.users]
        return data

    @classmethod
    def load(cls, usersinfo: List[str]) -> "UsersInfo":
        return UsersInfo(users=[UserInfo.load(userinfo) for userinfo in usersinfo])
