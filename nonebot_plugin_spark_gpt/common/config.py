import json
from typing import Dict, List
import nonebot
from pathlib import Path
from pydantic import BaseModel
import json


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
