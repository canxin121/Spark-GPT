from nonebot.log import logger
from EdgeGPT import Chatbot, ConversationStyle
from .source_data import newbing_persistor

class Newbing_api:
    def __init__(self,userdata):
        self.userdata = userdata

    async def __aenter__(self):
        if not self.userdata.chatbot:
            try:
                if len(newbing_persistor.proxy) > 0:
                    self.userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies,
                        proxy=newbing_persistor.proxy,
                    )
                else:
                    self.userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies
                    )
            except FileNotFoundError:
                logger.warning("newbing cookie未配置,无法使用，跳过")
                raise
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return

    async def refresh(self):
        retry = 3
        while retry > 0:
            try:
                if len(newbing_persistor.proxy) > 0:
                    self.userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies,
                        proxy=newbing_persistor.proxy,
                    )
                else:
                    self.userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies
                    )
                return
            except Exception as e:
                logger.error(str(e))
                if retry > 0:
                    retry += 1
                else:
                    raise e

    async def ask(self, question):
        chatbot = self.userdata.chatbot
        # 获取聊天模式
        chatmode = self.userdata.chatmode
        if chatmode == "1":
            style = ConversationStyle.creative
        elif chatmode == "2":
            style = ConversationStyle.balanced
        else:
            style = ConversationStyle.precise
        # 使用EdgeGPT进行ask询问
        retry = 3
        while retry > 0:
            try:
                if newbing_persistor.wss_link:
                    raw_json = await chatbot.ask(
                        prompt=question,
                        conversation_style=style,
                        wss_link=newbing_persistor.wss_link,
                    )
                    if raw_json["item"]:
                        return raw_json
                    else:
                        raise Exception("返回值为None")
                else:
                    raw_json = await chatbot.ask(
                        prompt=question, conversation_style=style
                    )
                    if raw_json["item"]:
                        return raw_json
                    else:
                        raise Exception("返回值为None")
            except Exception as e:
                logger.warning(str(e))
                if (
                    str(e) == "Update web page context failed"
                    or str(e) == "Conversation not found."
                    or str(e) == "InvalidRequest"
                ):
                    await self.refresh()
                    while retry > 0:
                        try:
                            if newbing_persistor.wss_link:
                                raw_json = await chatbot.ask(
                                    prompt=question,
                                    conversation_style=style,
                                    wss_link=newbing_persistor.wss_link,
                                )
                                if raw_json["item"]:
                                    return raw_json
                                else:
                                    raise Exception("返回值为None")
                            else:
                                raw_json = await chatbot.ask(
                                    prompt=question, conversation_style=style
                                )
                                if raw_json["item"]:
                                    return raw_json
                                else:
                                    raise Exception("返回值为None")
                        except:
                            if retry > 0:
                                retry -= 1
                            else:
                                raise e
                else:
                    if retry > 0:
                        retry -= 1
                    else:
                        raise e
