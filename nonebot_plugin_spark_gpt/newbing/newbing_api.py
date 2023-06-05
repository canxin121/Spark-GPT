from nonebot import logger

from .config import newbing_persistor, set_userdata
from .config import newbingtemper
from EdgeGPT import Chatbot, ConversationStyle


class Newbing_bot:
    def __init__(self, event):
        self.current_userinfo, self.current_userdata = set_userdata(
            event=event, user_data_dict=newbingtemper.user_data_dict
        )

    async def __aenter__(self):
        if not self.current_userdata.chatbot:
            try:
                if len(newbing_persistor.proxy) > 0:
                    self.current_userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies,
                        proxy=newbing_persistor.proxy,
                    )
                else:
                    self.current_userdata.chatbot = await Chatbot.create(
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
                    self.current_userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies,
                        proxy=newbing_persistor.proxy,
                    )
                else:
                    self.current_userdata.chatbot = await Chatbot.create(
                        cookies=newbing_persistor.cookies
                    )
                return
            except Exception as e:
                logger.error(e)
                if retry > 0:
                    retry += 1
                else:
                    raise e

    async def ask(self, question):
        chatbot = self.current_userdata.chatbot
        # 获取聊天模式
        chatmode = self.current_userdata.chatmode
        if chatmode == "1":
            style = ConversationStyle.creative
        elif chatmode == "2":
            style = ConversationStyle.balanced
        else:
            style = ConversationStyle.precise
        # 使用EdgeGPT进行ask询问
        retry = 3
        raw_json = {}
        while retry > 0:
            try:
                if newbing_persistor.wss_link:
                    raw_json = await chatbot.ask(
                        prompt=question,
                        conversation_style=style,
                        wss_link=newbing_persistor.wss_link,
                    )
                    return raw_json
                else:
                    raw_json = await chatbot.ask(
                        prompt=question, conversation_style=style
                    )
                    return raw_json
            except Exception as e:
                if str(e) == "Update web page context failed":
                    await self.refresh()
                    try:
                        await self.ask(question)
                    except Exception as e:
                        raise e
                else:
                    if retry > 0:
                        retry -= 1
                    else:
                        logger.warning(str(e))
                        raise e
