import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from nonebot.log import logger
import time
from ..common.config import config
from ..common.mytypes import BotData, BotInfo, CommonUserInfo
from ..common.user_data import common_users

SLACK_USER_TOKEN = ""
CHANNEL_ID = ""
CLAUDE_ID = ""
RECEIVE_INTERVAL = 2
ABLE = True
PRE_MSG = "<忽略'@Claude',删除'@Claude',不说没看到也不说看到>"


def load_config():
    global SLACK_USER_TOKEN, CHANNEL_ID, CLAUDE_ID, ABLE
    ABLE = True
    try:
        SLACK_USER_TOKEN = config.get_config("Claude Slack配置", "slack_user_token")
    except Exception as e:
        ABLE = False
        logger.warning(str(e))
    try:
        CHANNEL_ID = config.get_config("Claude Slack配置", "channel_id")
    except Exception as e:
        ABLE = False
        logger.warning(str(e))
    try:
        CLAUDE_ID = config.get_config("Claude Slack配置", "claude_id")
    except Exception as e:
        ABLE = False
        logger.warning(str(e))


load_config()

CLIENT = AsyncWebClient(token=SLACK_USER_TOKEN)


class Slack_Claude_Bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.lock = asyncio.Lock()
        self.nickname = bot_info.nickname

        self.botdata = bot_data
        self.common_userinfo = common_userinfo
        if not (SLACK_USER_TOKEN and CHANNEL_ID and CLAUDE_ID):
            raise Exception(
                "Claude Slack的配置项slack_user_token,CHANNEL_ID,claude_id没有填写全,无法使用"
            )

    def __hash__(self):
        return hash((self.nickname, self.common_userinfo.user_id))

    async def refresh(self):
        self.botdata.msg_ts = ""
        self.botdata.thread_ts = ""

        if self.botdata.prompt:
            try:
                _ = await self.claude_chat(question=self.botdata.prompt)

                return
            except Exception as e:
                error = f"Claude Slack刷新预设时error:{str(e)}"
                logger.error(error)
                raise Exception(error)
        else:
            common_users.save_userdata(self.common_userinfo)
            return

    async def ask(self, question: str):
        if not self.botdata.thread_ts and self.botdata.prompt:
            try:
                _ = await self.claude_chat(question=self.botdata.prompt)
            except Exception as e:
                error = f"Claude Slack加载预设时error:{str(e)}"
                logger.error(error)
                raise Exception(error)

        if self.botdata.prefix:
            question = self.botdata.prefix + "\n\n" + question
        try:
            answer = await self.claude_chat(question=question)

            return answer
        except Exception as e:
            error = f"Claude Slack询问时error:{str(e)}"
            logger.error(error)
            raise Exception(error)

    async def receive_message(self):
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            await asyncio.sleep(1)
            try:
                # 使用Web客户端调用conversations.replies方法
                result = await CLIENT.conversations_replies(
                    ts=self.botdata.thread_ts,
                    channel=CHANNEL_ID,
                    oldest=self.botdata.msg_ts,
                )
                result = result.data
                if (
                    not result
                    or len(result["messages"]) < 1
                    or result["messages"][-1]["user"] != CLAUDE_ID
                    or (
                        result["messages"][-1]["text"] == "_Typing…_"
                        or (
                            result["messages"][-1]["text"].startswith(
                                "\n&gt; _*Please note:*"
                            )
                            and result["messages"][-2]["text"] == "_Typing…_"
                        )
                    )
                ):
                    await asyncio.sleep(1)
                    raise Exception("slack的claude没有回复")
                elif "error" in result.keys():
                    raise Exception(result["error"])
                elif result["ok"]:
                    if result["messages"][-1]["text"].startswith(
                        "\n&gt; _*Please note:*"
                    ):
                        return result["messages"][-2]["text"]
                    else:
                        return result["messages"][-1]["text"]
                else:
                    raise Exception("未知错误")
            except Exception as e:
                detail_error = str(e)
                error = f"Claude Slack在获取消息到频道{CHANNEL_ID}时error: {e}"
                logger.error(error)
                retry -= 1
        raise Exception(detail_error)

    async def update_message(self, text: str):
        try:
            # 使用Web客户端调用chat.update方法
            result = await CLIENT.chat_update(
                channel=CHANNEL_ID,
                ts=self.botdata.msg_ts,
                text=f"<@{CLAUDE_ID}>{PRE_MSG}{text}",
            )
            return result
        except Exception as e:
            error = f"在更新发向claude的消息时error: {e}"
            logger.error(error)
            raise Exception(error)

    # 调用使用的api
    async def send_msg(self, msg: str):
        result = await CLIENT.chat_postMessage(
            channel=CHANNEL_ID,
            text=f"<@{CLAUDE_ID}>{PRE_MSG}{msg}",
            thread_ts=self.botdata.thread_ts,
        )
        if result["ok"]:
            return result["ts"]
        else:
            result = result["ok"]
            error = f"在发向claude的消息时error:{result}"
            logger.error(error)
            raise Exception(error)

    async def get_msg(self, question: str):
        response = "_Typing…_"
        retry = 3
        detail_error = "未知错误"
        while response.endswith("_Typing…_"):
            while retry > 0:
                try:
                    response = await self.receive_message()
                    if not response.endswith("_Typing…_"):
                        break
                except Exception as e:
                    detail_error = str(e)
                    if detail_error == "slack的claude没有回复":
                        await self.update_message(question)
                    retry -= 1
            if retry <= 0:
                raise Exception(detail_error)
        return response

    async def claude_chat(self, question: str):
        try:
            # new_ts可以理解为新发送的消息的id,而self.botdata.thread_ts则是一个消息列的id
            new_ts = await self.send_msg(question)
            self.botdata.msg_ts = new_ts
            if not self.botdata.thread_ts:
                self.botdata.thread_ts = new_ts
            common_users.save_userdata(common_userinfo=self.common_userinfo)
        except Exception as e:
            error = f"Claud Slack在发送消息时error:{str(e)}"
            logger.error(error)
            raise Exception(error)
        try:
            answer = await asyncio.wait_for(
                self.get_msg(question),
                timeout=120,
            )
            return answer
        except asyncio.TimeoutError as e:
            error = "Claude Slack在获取消息时超时"
            logger.error(error)
            raise Exception(error)
        except Exception as e:
            error = f"Claude Slack在获取消息时error{str(e)},如果多次无回复可以尝试刷新对话"
            logger.error(error)
            raise Exception(error)
