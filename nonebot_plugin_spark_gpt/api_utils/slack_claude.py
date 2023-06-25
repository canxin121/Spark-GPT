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
    try:
        SLACK_USER_TOKEN = config.get_config("Claude Slack配置", "slack_user_token")
    except Exception as e:
        logger.warning(str(e))
    try:
        CHANNEL_ID = config.get_config("Claude Slack配置", "channel_id")
    except Exception as e:
        logger.warning(str(e))
    try:
        CLAUDE_ID = config.get_config("Claude Slack配置", "claude_id")
    except Exception as e:
        logger.warning(str(e))


load_config()

CLIENT = AsyncWebClient(token=SLACK_USER_TOKEN)


class Slack_Claude_Bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.nickname = bot_info.nickname
        self.is_waiting = False
        self.bot_data = bot_data
        self.common_userinfo = common_userinfo
        if not (SLACK_USER_TOKEN and CHANNEL_ID and CLAUDE_ID):
            raise Exception(
                "Claude Slack的配置项slack_user_token,CHANNEL_ID,claude_id没有填写全,无法使用"
            )

    def __hash__(self):
        return hash(self.nickname)

    async def refresh(self):
        self.bot_data.msg_ts = ""
        self.bot_data.thread_ts = ""
        self.is_waiting = True
        try:
            _ = await self.claude_chat(question=self.bot_data.prompt)
            self.is_waiting = False
            return
        except Exception as e:
            self.is_waiting = False
            error = f"Claude Slack刷新时error:{str(e)}"
            logger.error(error)
            raise Exception(error)

    async def ask(self, question: str):
        self.is_waiting = True
        if not self.bot_data.thread_ts:
            try:
                _ = await self.claude_chat(question=self.bot_data.prompt)
            except Exception as e:
                self.is_waiting = False
                error = f"Claude Slack加载预设时error:{str(e)}"
                logger.error(error)
                raise Exception(error)
        try:
            answer = await self.claude_chat(question=question)
            self.is_waiting = False
            return answer
        except Exception as e:
            self.is_waiting = False
            error = f"Claude Slack询问时error:{str(e)}"
            logger.error(error)
            raise Exception(error)

    async def receive_message(self):
        try:
            # 使用Web客户端调用conversations.replies方法
            result = await CLIENT.conversations_replies(
                ts=self.bot_data.thread_ts,
                channel=CHANNEL_ID,
                oldest=self.bot_data.msg_ts,
            )
            return result
        except SlackApiError as e:
            error = f"Claude Slack在发送消息到频道{CHANNEL_ID}时error: {e}"
            logger.error(error)
            raise Exception(error)

    async def update_message(self, text: str):
        try:
            # 使用Web客户端调用chat.update方法
            result = await CLIENT.chat_update(
                channel=CHANNEL_ID,
                ts=self.bot_data.msg_ts,
                text=f"<@{CLAUDE_ID}>{text}",
            )
            return result
        except SlackApiError as e:
            error = f"Claude Slack在获取claude发送的消息时error: {e}"
            logger.error(error)
            raise Exception(error)

    # 调用使用的api
    async def send_msg(self, msg: str):
        result = await CLIENT.chat_postMessage(
            channel=CHANNEL_ID,
            text=f"<@{CLAUDE_ID}>{PRE_MSG}{msg}",
            thread_ts=self.bot_data.thread_ts,
        )
        if result["ok"]:
            return result["ts"]
        else:
            raise SlackApiError

    async def get_msg(self, question: str):
        response = "_Typing…_"
        start_time = time.time()
        max_retries = 5
        reties = 0
        while response.strip().endswith("_Typing…_"):
            time.sleep(RECEIVE_INTERVAL)
            replies = await self.receive_message()
            # 如果replies['ok']为False或消息列表长度小于等于1,则表示没有响应
            if not replies:
                raise SlackApiError("未收到Claude响应,请重试.")
            if not replies["ok"] or (
                time.time() - start_time > 10 and len(replies["messages"]) <= 1
            ):
                if replies["error"] == "ratelimited":
                    logger.error(f"Claude slack获取Clude发送的消息时被限速了,将在5秒后重试")
                    time.sleep(5)
                    continue
                # 如果重试次数超过{max_retries}次,则返回未响应
                # 否则更新消息从而触发@Claude的响应
                if reties >= max_retries:
                    # 解锁会话
                    raise f"以重试{max_retries}次,未收到Claude响应,请重试."
                else:
                    # 如果重试次数未超过{max_retries}次,则更新消息从而触发@Claude的响应
                    await self.update_message(CHANNEL_ID, self.bot_data, question)
                    start_time = time.time()
                    reties += 1
                    continue
            if len(replies["messages"]) <= 1:
                continue
            for index, message in enumerate(replies["messages"][1:], start=1):
                if message["user"] != CLAUDE_ID:
                    continue
                response = message["text"]
                if index < len(replies["messages"]) - 1 and any(
                    warn_tip in replies["messages"][index + 1]["text"]
                    for warn_tip in ["*Please note:*", "Oops! Claude was un"]
                ):
                    await CLIENT.chat_delete(
                        channel=CHANNEL_ID,
                        ts=replies["messages"][-1]["ts"],
                        as_user=True,
                    )
                break
        return response

    async def claude_chat(self, question: str):
        try:
            # new_ts可以理解为新发送的消息的id,而self.bot_data.thread_ts则是一个消息列的id
            new_ts = await self.send_msg(question)
            self.bot_data.msg_ts = new_ts
            if not self.bot_data.thread_ts:
                self.bot_data.thread_ts = new_ts
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
            error = f"Claude Slack在获取消息时error{str(e)}"
            logger.error(error)
            raise Exception(error)
