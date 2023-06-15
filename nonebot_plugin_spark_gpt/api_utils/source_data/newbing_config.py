import json
from typing import List
import nonebot
from pathlib import Path
from pydantic import BaseModel
from ..common.config import spark_persistor


# 储存newbing的数据,不需要本地保存,每次启动从env读取覆盖即可
class NewBing_Config(BaseModel):
    cookie_path_: str = str(Path()) + "/data/spark_gpt/newbing_cookie.json"
    cookies: List[dict] = []
    pic_able: str = None
    url_able: str = "True"
    suggest_able: str = "True"
    num_limit: int = 350
    proxy: str = ""
    predownload: str = "True"
    forward: str = "True"
    blacklist: List[str] = []
    whitelist: List[str] = []
    wss_link: str = "wss://sydney.bing.com/sydney/ChatHub"
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
        self.predownload = getattr(get_config, "newbing_predownload", self.predownload)
        self.forward = getattr(get_config, "newbing_forward", self.forward)
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
newbing_config = NewBing_Config()
