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


# 储存Spark_Desk_的持久数据,提供一键保存和加载功能
class Spark_Desk_Config(BaseModel):
    path_: str = str(Path()) + "/data/spark_gpt/spark_desk_data.json"
    session_token_path: str = (
        str(Path()) + "/data/spark_gpt/spark_desk_session_token.txt"
    )
    session_token: str = ""
    pic_able: str = None
    url_able: str = "True"
    num_limit: int = 350
    mode: str = "black"
    cookie: str = ""
    fd: str = ""
    GtToken: str = ""
    sid: str = ""
    superusers = []
    blacklist = []
    whitelist = []
    # user_dict: Dict[UserInfo, Dict["all" or "now", Dict[nickname, BotInfo]]] = {}

    def __init__(self, **data):
        super().__init__(**data)
        try:
            saved_data = self.load()
            self.__dict__.update(saved_data)
        except:
            pass
        get_config = nonebot.get_driver().config
        self.superusers = (
            get_config.spark_desk_superusers
            if hasattr(get_config, "spark_desk_superusers")
            else spark_persistor.superusers
        )
        self.blacklist = (
            get_config.spark_desk_blacklist
            if hasattr(get_config, "spark_desk_blacklist")
            else spark_persistor.blacklist
        )
        self.whitelist = (
            get_config.spark_desk_whitelist
            if hasattr(get_config, "spark_desk_whitelist")
            else spark_persistor.whitelist
        )
        self.mode = (
            get_config.spark_desk_mode
            if hasattr(get_config, "spark_desk_mode")
            and get_config.spark_desk_mode in ["white", "black"]
            else spark_persistor.mode
        )
        self.pic_able = getattr(
            get_config, "spark_desk_picable", spark_persistor.pic_able
        )
        self.url_able = getattr(
            get_config, "spark_desk_urlable", spark_persistor.url_able
        )
        self.num_limit = int(
            getattr(get_config, "spark_desk_limit", spark_persistor.num_limit)
        )
        self.cookie = getattr(get_config, "spark_desk_cookie", self.cookie)
        self.fd = getattr(get_config, "spark_desk_fd", self.fd)
        self.GtToken = getattr(get_config, "spark_desk_gttoken", self.GtToken)
        self.sid = getattr(get_config, "spark_desk_sid", self.sid)
        self.save()

# 这里的配置即使在多平台，也应只初始化一次
spark_desk_config = Spark_Desk_Config()
