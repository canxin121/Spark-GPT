import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

CONFIG_SOURCE = (
    Literal[
        "总控配置",
        "Newbing配置",
        "Spark Desk配置",
        "Chat GPT web配置",
        "Claude Slack配置",
        "Poe配置",
        "Bard配置",
        "通义千问配置",
        "Claude Ai配置",
    ],
)
CONFIG_NAMES = (
    Literal[
        "__Secure-1PSID",
        "superusers",
        "cookie",
        "proxy",
        "pic_able",
        "url_able",
        "suggest_able",
        "num_limit",
        "mode",
        "wss_link",
        "cookie",
        "fd",
        "GtToken",
        "sid",
        "session token",
        "model",
        "api_url",
        "channel_id",
        "claude_id",
        "slack_user_token",
        "XSRF_TOKEN",
        "specialpic_width",
        "pic_width",
        "public_command",
        "private_command",
        "wait_msg_able",
    ],
)


class Config(BaseModel):
    path: Path = Field(None, description="配置文件的存储路径")
    config: dict = Field(None, description="配置文件的内容")

    def __init__(self, **data):
        super().__init__(**data)
        self.path = Path() / "data/spark_gpt/common"
        # 配置的优先级是 分级配置>总控配置，及当分级配置没有填写时从总控配置中读取
        self.config = {
            "总控配置": {
                "superusers": "[]",
                "pic_able": "Auto",
                "url_able": "True",
                "wait_msg_able": "True",
                "num_limit": "500",
                "pic_width": "1800",
                "specialpic_width": "400",
                "private_command": "/",
                "public_command": ".",
            },
            "Newbing配置": {
                "cookie": "",
                "proxy": "",
                "wss_link": "wss://sydney.bing.com/sydney/ChatHub",
            },
            "Spark Desk配置": {
                "cookie": "",
                "fd": "",
                "GtToken": "",
                "sid": "",
            },
            "Chat GPT web配置": {
                "session token": "",
                "proxy": "",
                "model": "text-davinci-002-render-sha",
                "api_url": "https://chat.loli.vet/",
            },
            "Claude Slack配置": {
                "slack_user_token": "",
                "claude_id": "",
                "channel_id": "",
            }, "Claude Ai配置": {
                "cookie": "",
                "organization_uuid": "",
                "proxy": "",
            },
            "Poe配置": {
                "cookie": "",
                "proxy": "",
            },
            "Bard配置": {
                "__Secure-1PSID": "",
                "proxy": "",
            },
            "通义千问配置": {
                "cookie": "",
                "XSRF_TOKEN": "",
            },

        }
        self.load()
        self.save()

    def change_config(
            self, source: CONFIG_SOURCE, config_name: CONFIG_NAMES, config: str
    ):
        """修改配置项"""
        if source in self.config.keys():
            if config_name in self.config[source].keys():
                if self.config[source]:
                    self.config[source][config_name] = config
                    self.save()
                else:
                    raise Exception("未知错误")
            else:
                raise Exception("没有这个配置项")
        else:
            raise Exception("没有这个来源的配置")
        self.save()

    def get_config(self, source: CONFIG_SOURCE, config_name: CONFIG_NAMES):
        """获取配置项"""
        if source in self.config.keys():
            if config_name in self.config[source].keys():
                if (
                        config_name in self.config[source]
                        and self.config[source][config_name]
                ):
                    return self.config[source][config_name]
                elif config_name in self.config["总控配置"]:
                    return self.config["总控配置"][config_name]
                else:
                    raise Exception(f"总控配置和该配置均没有非空的{config_name}配置项")
            else:
                raise Exception(f"没有{config_name}配置项")
        else:
            raise Exception(f"没有{source}来源的配置")

    def load(self):
        """从本地读取配置项"""
        self.path.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.path / "config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for eachdict in data.keys():
                    for key in data[eachdict].keys():
                        if key in self.config[eachdict].keys():
                            self.config[eachdict][key] = data[eachdict][key]
        except Exception as e:
            # logger.error(str(e))
            pass

    def save(self):
        """将配置项保存到本地"""
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "config.json").touch()
        try:
            with open(self.path / "config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False)
        except Exception:
            # logger.error(str(e))
            pass


config = Config()
