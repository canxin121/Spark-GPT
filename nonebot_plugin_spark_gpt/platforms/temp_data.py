from typing import Literal, Dict
from nonebot import logger
from pathlib import Path
from pydantic import BaseModel
from bidict import bidict
import json
from ..common.mytypes import CommonUserInfo, BotInfo, BotData, PLATFORM, SOURCE
from ..common.user_data import common_users
from ..api_utils.spark_desk import SparkBot
from ..api_utils.newbing import Newbing_bot
from ..api_utils.chatgpt_web import ChatGPT_web_Bot
from ..api_utils.slack_claude import Slack_Claude_Bot
from ..api_utils.Poe import Poe_bot
from ..api_utils.bard import Bard_Bot


class Bot_Links:
    msg_bot_dict: bidict = bidict()
    bot_dict: Dict[str, any] = {}


class Temp_Bots:
    users: Dict[CommonUserInfo, Bot_Links] = {}

    def __init__(self):
        self.users: Dict[CommonUserInfo, Bot_Links] = {}

    def set_bot_msgid(
        self, common_userinfo: CommonUserInfo, bot: any, new_message_id: str
    ):
        botlinks: Bot_Links = self.get_bot_links(common_userinfo)
        if bot:
            botlinks.msg_bot_dict.inv[bot] = new_message_id
        else:
            raise Exception("没有这个bot")

    def del_bot_by_msgid(self, common_userinfo: CommonUserInfo, message_id: str):
        botlinks: Bot_Links = self.get_bot_links(common_userinfo=common_userinfo)
        if message_id in botlinks.msg_bot_dict.keys():
            del botlinks.msg_bot_dict[message_id]
        else:
            raise Exception("没有这个messageid对应的bot")

    def get_bot_by_msgid(self, common_userinfo: CommonUserInfo, message_id: str):
        botlinks: Bot_Links = self.get_bot_links(common_userinfo)
        if str(message_id) in botlinks.msg_bot_dict.keys():
            return botlinks.msg_bot_dict[str(message_id)]
        else:
            raise Exception("没有这个messageid对应的bot")

    def get_bot_by_text(self, common_userinfo: CommonUserInfo, text: str):
        try:
            botinfo, botdata = common_users.get_bot_by_text(common_userinfo, text)
        except Exception as e:
            raise
        try:
            return text.replace(f"/{botinfo.nickname}", "").replace(
                f".{botinfo.nickname}", ""
            ), self.get_bot_by_botinfo(
                common_userinfo=common_userinfo, bot_info=botinfo
            )
        except:
            self.load_user_bot(
                common_userinfo=common_userinfo, botinfo=botinfo, botdata=botdata
            )
            return text.replace(f"/{botinfo.nickname}", "").replace(
                f".{botinfo.nickname}", ""
            ), self.get_bot_by_botinfo(
                common_userinfo=common_userinfo, bot_info=botinfo
            )

    def load_user_bot(
        self, common_userinfo: CommonUserInfo, botinfo: BotInfo, botdata: BotData
    ):
        bot_links: Bot_Links = self.get_bot_links(common_userinfo=common_userinfo)
        if botdata.source == "spark desk":
            bot_links.bot_dict[botinfo] = SparkBot(
                common_userinfo=common_userinfo, bot_info=botinfo, bot_data=botdata
            )
        elif botdata.source == "bing":
            bot_links.bot_dict[botinfo] = Newbing_bot(
                common_userinfo=common_userinfo, bot_info=botinfo, bot_data=botdata
            )
        elif botdata.source == "chatgpt web":
            bot_links.bot_dict[botinfo] = ChatGPT_web_Bot(
                common_userinfo=common_userinfo, bot_info=botinfo, bot_data=botdata
            )
        elif botdata.source == "slack claude":
            bot_links.bot_dict[botinfo] = Slack_Claude_Bot(
                common_userinfo=common_userinfo, bot_info=botinfo, bot_data=botdata
            )
        elif botdata.source == "poe chatgpt" or botdata.source == "poe claude":
            bot_links.bot_dict[botinfo] = Poe_bot(
                common_userinfo=common_userinfo, bot_info=botinfo, bot_data=botdata
            )
        elif botdata.source == "bard":
            bot_links.bot_dict[botinfo] = Bard_Bot(
                common_userinfo=common_userinfo, bot_info=botinfo, bot_data=botdata
            )

    def add_new_bot(
        self,
        common_userinfo: CommonUserInfo,
        botinfo: BotInfo,
        botdata: BotData,
    ):
        common_users.add_new_bot(
            common_userinfo=common_userinfo,
            botinfo=botinfo,
            botdata=botdata,
        )
        self.load_user_bot(
            common_userinfo=common_userinfo, botinfo=botinfo, botdata=botdata
        )

    def get_bot_by_botinfo(self, common_userinfo: CommonUserInfo, bot_info: BotInfo):
        bot_links: Bot_Links = self.get_bot_links(common_userinfo=common_userinfo)
        if bot_info in bot_links.bot_dict.keys():
            return bot_links.bot_dict[bot_info]
        else:
            raise Exception("Temp_Bots中没有这个bot")

    def get_bot_links(self, common_userinfo: CommonUserInfo):
        if common_userinfo in self.users.keys():
            return self.users[common_userinfo]
        else:
            self.users[common_userinfo] = Bot_Links()
            return self.users[common_userinfo]


temp_bots = Temp_Bots()
