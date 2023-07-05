import asyncio
from typing import Dict, Literal
from nonebot.log import logger
from pydantic import BaseModel
from ..common.config import config
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from ..common.mytypes import CommonUserData, CommonUserInfo, BotData, BotInfo
from ..common.user_data import common_users
import json

PROXY = ""
COOKIES = ""
WSS_LINK = ""
ABLE = True


def load_config():
    global PROXY, COOKIES, WSS_LINK, ABLE
    ABLE = True
    try:
        PROXY = config.get_config(source="Newbing配置", config_name="proxy")
    except Exception as e:
        logger.warning(f"加载Newbing配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")

    try:
        cookie_str = config.get_config(source="Newbing配置", config_name="cookie")
        COOKIES = json.loads(cookie_str)
    except Exception as e:
        logger.warning(f"加载Newbing配置时warn:{str(e)},没有填写Newbing的Cookie的情况下只能连续对话5次")

    try:
        WSS_LINK = config.get_config(source="Newbing配置", config_name="wss_link")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Newbing配置时warn:{str(e)}")


load_config()


class Newbing_bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.nickname = bot_info.nickname
        self.common_userinfo = common_userinfo
        self.chatbot: Chatbot = None
        self.chatstyle: ConversationStyle = ConversationStyle.creative
        self.lock = asyncio.Lock()
        self.botdata = bot_data

    def __hash__(self) -> int:
        return hash((self.nickname, self.common_userinfo.user_id))

    async def refresh(self):
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                if len(PROXY) > 0:
                    self.chatbot = await Chatbot.create(cookies=COOKIES, proxy=PROXY)
                else:
                    self.chatbot = await Chatbot.create(cookies=COOKIES)
                return
            except Exception as e:
                retry -= 1
                detail_error = str(e)
                logger.error(f"Newbing刷新时error:{detail_error}")
        error = f"Newbing刷新时报错次数超过上限{detail_error}"
        logger.error(error)
        raise Exception(error)

    async def ask(self, question):
        if question in ["creative", "创造", "balanced", "均衡", "precise", "精确"]:
            self.change_style(question)
        if not self.chatbot:
            await self.refresh()
        if question in ["1", "2", "3"] and self.botdata.last_suggests:
            question = self.botdata.last_suggests[int(question) - 1]
        if self.botdata.prefix:
            question = self.botdata.prefix + "\n\n" + question
        retry = 3
        detail_error = "未知错误"
        while retry >= 0:
            try:
                raw_json = await asyncio.wait_for(
                    self.chatbot.ask(
                        prompt=question,
                        conversation_style=ConversationStyle.creative,
                        simplify_response=True,
                        wss_link=WSS_LINK,
                        locale="en-us",
                    ),
                    timeout=360,
                )
                left, source_text, suggests = (
                    str(raw_json["messages_left"]),
                    "",
                    raw_json["suggestions"],
                )
                self.botdata.last_suggests = suggests
                if raw_json["sources_text"][:4] != raw_json["text"][:4]:
                    source_text = raw_json["sources_text"] + "\n"
                suggest_str = "\n".join([f"{i+1}:{s}" for i, s in enumerate(suggests)])
                answer = f"{raw_json['text'].replace('[^', '[').replace('^]', ']').replace('**', '')}\n\n{source_text}建议回复:\n{suggest_str}\n\n剩余{left}条连续对话"
                return answer
            except asyncio.TimeoutError:
                error = "Newbing在询问时超时无响应"
                logger.error(error)
                raise Exception(error)
            except Exception as e:
                detail_error = str(e)
                logger.warning(f"Newbing在询问时出错{detail_error}")
                if str(e) == "Max messages reached" or str(e) == "No message found":
                    await self.refresh()
                    while retry > 0:
                        try:
                            raw_json = await asyncio.wait_for(
                                self.chatbot.ask(
                                    prompt=question,
                                    conversation_style=ConversationStyle.creative,
                                    simplify_response=True,
                                    wss_link=WSS_LINK,
                                    locale="en-us",
                                ),
                                timeout=360,
                            )
                            left, source_text, suggests = (
                                str(raw_json["messages_left"]),
                                "",
                                raw_json["suggestions"],
                            )
                            if raw_json["sources_text"][:4] != raw_json["text"][:4]:
                                source_text = raw_json["sources_text"] + "\n"
                            suggest_str = "\n".join(
                                [f"{i+1}:{s}" for i, s in enumerate(suggests)]
                            )
                            answer = f"{raw_json['text'].replace('[^', '[').replace('^]', ']').replace('**', '')}\n{source_text}建议回复:\n{suggest_str}\n剩余{left}条连续对话"
                            return answer
                        except asyncio.TimeoutError:
                            error = "Newbing在询问时超时无响应"
                            logger.error(error)
                            raise Exception(error)
                        except Exception as e:
                            detail_error = str(e)
                            logger.error(f"newbing在询问时出错{detail_error}")
                            retry -= 1
                else:
                    retry -= 1
        error = f"Newbing询问时出错超过最大尝试数:{detail_error}"
        logger.error(error)
        raise Exception(error)

    def change_style(self, chat_style_str: str):
        if chat_style_str in ["creative", "创造"]:
            self.chatstyle = ConversationStyle.creative
        elif chat_style_str in ["balanced", "均衡"]:
            self.chatstyle = ConversationStyle.balanced
        elif chat_style_str in ["precise", "精确"]:
            self.chatstyle == ConversationStyle.precise
        common_users.save_userdata(common_userinfo=self.common_userinfo)
        return
