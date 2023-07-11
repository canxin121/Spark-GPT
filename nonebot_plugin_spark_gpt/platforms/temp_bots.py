from typing import Any, Dict, Union

from bidict import bidict
from pydantic import BaseModel, Field

from .nonebot.utils import OB11_BOT, Bot, MessageEvent, TGBot, KOOKBot,DISCORD_Bot
from ..chatbot.poe import Poe_bot
from ..chatbot.bard import Bard_Bot
from ..chatbot.chatgpt_web import ChatGPT_web_Bot
from ..chatbot.newbing import Newbing_bot
from ..chatbot.slack_claude import Slack_Claude_Bot
from ..chatbot.spark_desk import SparkBot
from ..chatbot.tongyiqianwen import TongYiQianWen
from ..chatbot.sydneybing import SydneyBing_bot
from ..common.mytypes import CommonUserInfo, BotInfo, BotData
from ..common.user_data import common_users

CHATBOT = Union[
    SparkBot,
    Newbing_bot,
    SydneyBing_bot,
    ChatGPT_web_Bot,
    Slack_Claude_Bot,
    Poe_bot,
    Bard_Bot,
    TongYiQianWen,
]


class Bot_Links(BaseModel):
    msg_bot_dict: bidict[str, Any] = Field(None, description="储存信息和chatbot的双向dict")
    bot_dict: Dict[str, Any] = Field(None, description="储存用户和其chatbot的dict")

    def __init__(self, **data):
        super().__init__(**data)
        self.msg_bot_dict: bidict = data.get("msg_bot_dict") or bidict()
        self.bot_dict: Dict[str, Any] = data.get("bot_dict") or bidict()


class Temp_Bots(BaseModel):
    users: Dict[CommonUserInfo, Bot_Links] = Field(
        None, description="储存运行中创建和使用的chatbot"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.users: Dict[CommonUserInfo, Bot_Links] = data.get("users") or {}

    def get_message_id_by_send(
        self,
        event: MessageEvent,
        reply: any,
        bot: Bot,
    ):
        try:
            if isinstance(bot, OB11_BOT):
                return str(reply["message_id"])
            elif isinstance(bot, TGBot):
                return str(reply.message_id + event.from_.id)
            elif isinstance(bot, KOOKBot):
                return str(reply.msg_id)
            elif isinstance(bot, DISCORD_Bot):
                return str(reply.id)
        except:
            pass

    def get_message_id_by_get(self, bot: Bot, event: MessageEvent):
        if isinstance(bot, OB11_BOT):
            return str(event.reply.message_id)
        elif isinstance(bot, TGBot):
            return str(event.reply_to_message.message_id + event.from_.id)
        elif isinstance(bot, KOOKBot):
            return str(event.msg_id)
        elif isinstance(bot,DISCORD_Bot):
            return str(event.reply.id)

    def set_bot_msgid(
        self,
        common_userinfo: CommonUserInfo,
        chatbot: CHATBOT,
        bot: Bot,
        event: MessageEvent,
        reply: any,
    ):
        botlinks: Bot_Links = self.get_bot_links(common_userinfo)
        if chatbot:
            botlinks.msg_bot_dict.inv[chatbot] = self.get_message_id_by_send(
                event, reply, bot
            )
        else:
            raise Exception("没有这个bot")

    def get_bot_by_msgid(
        self,
        common_userinfo: CommonUserInfo,
        bot: Bot,
        event: MessageEvent,
        kook_msgid: str = "",
    ):
        botlinks: Bot_Links = self.get_bot_links(common_userinfo)
        if kook_msgid:
            message_id = kook_msgid
        else:
            message_id = self.get_message_id_by_get(bot, event)
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
        elif botdata.source == "sydneybing":
            bot_links.bot_dict[botinfo] = SydneyBing_bot(
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
        elif botdata.source == "通义千问":
            bot_links.bot_dict[botinfo] = TongYiQianWen(
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
