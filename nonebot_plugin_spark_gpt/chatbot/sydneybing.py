import asyncio
import json
from SydneyGPT.SydneyGPT import Chatbot
from EdgeGPT.EdgeGPT import ConversationStyle
from typing import Literal
from nonebot.log import logger
from ..common.config import config
from ..common.mytypes import CommonUserData, CommonUserInfo, BotData, BotInfo
from ..common.user_data import common_users


class SydneyBing_bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.nickname = bot_info.nickname
        self.common_userinfo = common_userinfo
        self.botdata = bot_data
        self.chatbot: Chatbot = None
        self.chatstyle: ConversationStyle = ConversationStyle.creative
        self.lock = asyncio.Lock()

    def __hash__(self) -> int:
        return hash((self.nickname, self.common_userinfo.user_id))

    async def refresh(self):
        from .newbing import PROXY, COOKIES, WSS_LINK

        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                if len(PROXY) > 0:
                    self.chatbot = await Chatbot.create(cookies=COOKIES, proxy=PROXY)
                else:
                    self.chatbot = await Chatbot.create(cookies=COOKIES)
                break
            except Exception as e:
                detail_error = str(e)
                logger.error(f"Sydneybing刷新时error:{detail_error}")
                retry -= 1
        if retry <= 0:
            error = f"Sydneybing刷新报错次数超过上限:{detail_error}"
            logger.error(error)
            raise Exception(error)
        if self.botdata.prompt and self.chatbot:
            if retry <= 0:
                error = f"Sydneybing刷新时报错次数超过上限{detail_error}"
                logger.error(error)
                raise Exception(error)
            if len(self.botdata.prompt) > 4000:
                raise Exception("Sydney的预设长度不得超过4000,请重新创建")
            else:
                retry = 2
                detail_error = "未知错误"
                while retry > 0:
                    try:
                        _ = await asyncio.wait_for(
                            self.chatbot.ask(
                                prompt=self.botdata.prompt,
                                conversation_style=ConversationStyle.creative,
                                simplify_response=True,
                                wss_link=WSS_LINK,
                                locale="en-us",
                            ),
                            timeout=360,
                        )
                        return
                    except asyncio.TimeoutError:
                        error = "Sydneybing在初始化预设时超时无响应"
                        logger.error(error)
                        raise Exception(error)
                    except Exception as e:
                        detail_error = str(e)
                        logger.error(f"Sydneybing在初始化预设时error:{detail_error}")
                        retry -= 1
            error = f"Sydneybing在初始化预设时出错次数超过上限{detail_error}"
            logger.error(error)
            raise Exception(error)
        else:
            return

    async def ask(self, question):
        from .newbing import WSS_LINK

        if question in ["creative", "创造", "balanced", "均衡", "precise", "精确"]:
            self.change_style(question)
        if not self.chatbot:
            await self.refresh()
        if question in ["1", "2", "3"] and self.botdata.last_suggests:
            question = self.botdata.last_suggests[int(question) - 1]

        if self.botdata.prefix:
            question = self.botdata.prefix + "\n" + question

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
                if raw_json["sources_text"][:4] != raw_json["text"][:4]:
                    source_text = raw_json["sources_text"] + "\n"
                suggest_str = "\n".join([f"{i+1}:{s}" for i, s in enumerate(suggests)])
                answer = f"{raw_json['text'].replace('[^', '[').replace('^]', ']').replace('**', '')}\n\n{source_text}建议回复:\n{suggest_str}\n\n剩余{left}条连续对话"
                return answer
            except asyncio.TimeoutError:
                error = "Sydneybing在询问时超时无响应"
                logger.error(error)
                raise Exception(error)
            except Exception as e:
                detail_error = str(e)
                logger.warning(f"Sydneybing在询问时出错{detail_error}")
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
                            error = "Sydneybing在询问时超时无响应"
                            logger.error(error)
                            raise Exception(error)
                        except Exception as e:
                            detail_error = str(e)
                            logger.error(f"SydenyBing在询问时出错:{detail_error}")
                            retry -= 1
                else:
                    retry -= 1
        error = f"Sydneybing询问时出错超过最大尝试数:{detail_error}"
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
