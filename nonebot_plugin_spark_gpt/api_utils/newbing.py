from typing import Dict, Literal
from nonebot.log import logger
from pydantic import BaseModel
from ..common.config import config
from EdgeGPT import Chatbot, ConversationStyle, ConversationStyle
from ..common.mytypes import CommonUserInfo, BotData, BotInfo
from ..common.user_data import common_users
import json

PROXY = ""
COOKIES = ""
WSS_LINK = ""
ABLE = True


def load_config():
    global PROXY, COOKIES, WSS_LINK,ABLE
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
        self.is_waiting = False
        self.nickname = bot_info.nickname
        self.chatbot: Chatbot = None
        self.chatstyle: ConversationStyle = ConversationStyle.creative

    def __hash__(self) -> int:
        return hash(self.nickname)

    async def refresh(self):
        retry = 3
        self.is_waiting = True
        while retry > 0:
            try:
                if len(PROXY) > 0:
                    self.chatbot = Chatbot(
                        cookies=COOKIES,
                        proxy=PROXY,
                    )
                else:
                    self.chatbot = Chatbot(cookies=COOKIES)
                self.is_waiting = False
                return
            except Exception as e:
                logger.error(f"Newbing刷新时error:{str(e)}")
                if retry > 0:
                    retry += 1
                else:
                    self.is_waiting = False
                    raise e
        error = "Newbing刷新时报错次数超过上限"
        logger.error(error)
        raise Exception(error)

    async def generate_answer(self, raw_json: dict):
        value = raw_json["item"]["result"]["value"]
        if value != "Success":
            if value == "Throttled":
                return "该账号cookie问答次数已达到今日上限"
            else:
                return f"出错喽:{value}，多次失败请尝试刷新对话"
        reply = ""
        last_num = len(raw_json["item"]["messages"]) - 1
        try:
            max_num = raw_json["item"]["throttling"]["maxNumUserMessagesInConversation"]
            now_num = raw_json["item"]["throttling"]["numUserMessagesInConversation"]
            if "messageType" in raw_json["item"]["messages"][last_num]:
                last_num -= 1
            reply = raw_json["item"]["messages"][last_num]["text"]
            reply = (
                reply.replace("&#91;", "[")
                .replace("&#93;", "]")
                .replace("[^", "[")
                .replace("^]", "]")
            )

        except:
            raise Exception("解析回复时出错")
        try:
            is_offense = raw_json["item"]["messages"][0]["offense"]

            if is_offense == "Offensive" and not reply:
                return "你的询问太冒犯了,newbing拒绝回答"
            if "hiddenText" in raw_json["item"]["messages"][last_num] and not reply:
                return "你的询问太敏感了,newbing拒绝回答"
        except:
            raise Exception("解析回复时出错")
        suggest_str = "\n建议回复:\n"
        try:
            suggests = [
                raw_json["item"]["messages"][last_num]["suggestedResponses"][i]["text"]
                for i in range(
                    len(raw_json["item"]["messages"][last_num]["suggestedResponses"])
                )
            ]
            suggest_str += "\n".join(
                [f"{i+1}. {suggestion}  " for i, suggestion in enumerate(suggests)]
            )
        except:
            suggests = []
            pass
        limit_str = f"\n回复上限:{now_num}/{max_num}  "
        if now_num == max_num:
            try:
                await self.refresh()
            except Exception as e:
                logger.error("Newbing自动刷新出错:" + str(e))
                pass
        final_answer = str(reply + "\n" + suggest_str + limit_str)
        self.is_waiting = False
        return final_answer

    async def ask(self, question):
        if not self.chatbot:
            await self.refresh()
        # 使用EdgeGPT进行ask询问
        retry = 3
        self.is_waiting = True
        while retry >= 0:
            try:
                raw_json = await self.chatbot.ask(
                    prompt=question,
                    conversation_style=self.chatstyle,
                    wss_link=WSS_LINK,
                )

                if raw_json["item"]:
                    if raw_json["item"]["result"]["value"] == "InvalidSession":
                        raise Exception("InvalidSession")
                    elif raw_json["item"]["result"]["value"] == "UnauthorizedRequest":
                        raise Exception("UnauthorizedRequest")
                    self.is_waiting = False
                    return await self.generate_answer(raw_json)
                else:
                    raise Exception("返回值为None")
            except Exception as e:
                logger.warning(str(e))
                if (
                    str(e) == "Update web page context failed"
                    or str(e) == "Conversation not found."
                    or str(e) == "InvalidRequest"
                    or str(e) == "InvalidSession"
                    or str(e) == "UnauthorizedRequest"
                ):
                    await self.refresh()
                    self.is_waiting = True
                    while retry > 0:
                        try:
                            if WSS_LINK:
                                raw_json = await self.chatbot.ask(
                                    prompt=question,
                                    conversation_style=self.chatstyle,
                                    wss_link=WSS_LINK,
                                )
                                if raw_json["item"]:
                                    self.is_waiting = False
                                    return await self.generate_answer(raw_json)
                                else:
                                    raise Exception("返回值为None")
                            else:
                                raw_json = await self.chatbot.ask(
                                    prompt=question, conversation_style=self.chatstyle
                                )
                                if raw_json["item"]:
                                    self.is_waiting = False
                                    return await self.generate_answer(raw_json)
                                else:
                                    raise Exception("返回值为None")
                        except:
                            self.is_waiting = False
                            if retry > 0:
                                retry -= 1
                            else:
                                raise e
                else:
                    if retry > 0:
                        retry -= 1
                    else:
                        raise e
        error = "Newbing询问时出错超过最大尝试数"
        logger.error(error)
        raise Exception(error)

    def change_style(self, chat_style_index: Literal["1", "2", "3"]):
        if chat_style_index == "1":
            self.chatstyle = ConversationStyle.creative
        elif chat_style_index == "2":
            self.chatstyle = ConversationStyle.balanced
        else:
            self.chatstyle == ConversationStyle.precise
        return
