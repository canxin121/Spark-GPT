import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from nonebot import logger
from .config import BotInfo, claude_slack_persistor
from .claude_func import random_uuid4
import time


SLACK_USER_TOKEN = claude_slack_persistor.slack_user_token
CHANNEL_ID = claude_slack_persistor.channel_id
CLAUDE_ID = claude_slack_persistor.claude_id
RECEIVE_INTERVAL = 2

# 实例化一个Client
if claude_slack_persistor.proxy:
    client = AsyncWebClient(token=SLACK_USER_TOKEN, proxy=claude_slack_persistor.proxy)
else:
    client = AsyncWebClient(token=SLACK_USER_TOKEN, proxy=claude_slack_persistor.proxy)


async def receive_message(time_stamp, thread_ts, channel_id):
    try:
        # 使用Web客户端调用conversations.replies方法
        result = await client.conversations_replies(
            ts=thread_ts, channel=channel_id, oldest=time_stamp
        )
        return result
    except SlackApiError as e:
        print(f"Error posting message to channel {channel_id}: {e}")


async def update_message(channel_id, ts, text: str):
    try:
        # 使用Web客户端调用chat.update方法
        result = await client.chat_update(
            channel=channel_id, ts=ts, text=f"<@{CLAUDE_ID}>{text}"
        )
        return result
    except SlackApiError as e:
        print(f"Error posting message to channel {channel_id}: {e}")


# 调用使用的api
async def send_msg(msg: str, thread_ts: str = None):
    result = await client.chat_postMessage(
        channel=CHANNEL_ID, text=f"<@{CLAUDE_ID}>{msg}", thread_ts=thread_ts
    )
    if result["ok"]:
        return result["ts"]
    else:
        raise SlackApiError


async def get_msg(time_stamp, thread_ts):
    response = "_Typing…_"
    start_time = time.time()
    max_retries = 5
    reties = 0
    while response.strip().endswith("_Typing…_"):
        time.sleep(RECEIVE_INTERVAL)
        replies = await receive_message(time_stamp, thread_ts, CHANNEL_ID)
        # 如果replies['ok']为False或消息列表长度小于等于1，则表示没有响应
        if not replies:
            raise SlackApiError("未收到Claude响应，请重试。")
        if not replies["ok"] or (
            time.time() - start_time > 10 and len(replies["messages"]) <= 1
        ):
            if replies["error"] == "ratelimited":
                print(f"被限速了， 将在5秒后重试...")
                time.sleep(5)
                continue
            # 如果重试次数超过{max_retries}次，则返回未响应
            # 否则更新消息从而触发@Claude的响应
            if reties >= max_retries:
                # 解锁会话
                raise f"以重试{max_retries}次，未收到Claude响应，请重试。"
            else:
                # 如果重试次数未超过{max_retries}次，则更新消息从而触发@Claude的响应
                # await update_message(CHANNEL_ID, ts, msg)
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
                await client.chat_delete(
                    channel=CHANNEL_ID,
                    ts=replies["messages"][-1]["ts"],
                    as_user=True,
                )
            break
    return response


async def claude_chat(msg, botinfo: BotInfo):
    thread_ts = botinfo.thread_ts
    try:
        # new_ts可以理解为新发送的消息的id，而thread_ts则是一个消息列的id
        new_ts = await send_msg(msg, thread_ts)
        botinfo.time_stamp = new_ts
        if not botinfo.thread_ts:
            botinfo.thread_ts = new_ts
    except Exception as e:
        return e
    response = await asyncio.wait_for(get_msg(new_ts, botinfo.thread_ts),timeout=120)
    return response, botinfo
