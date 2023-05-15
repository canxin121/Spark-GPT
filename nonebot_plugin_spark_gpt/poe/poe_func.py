import datetime
from typing import Union
import re, uuid, asyncio, string, random
from .config import poe_persistor
from nonebot import logger, require

require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from ..common.render.render import md_to_pic
from ..common.common_func import get_url


async def if_quit(msg, matcher):
    if msg in ["取消", "算了"]:
        await matcher.send("终止添加")


def reply_out(
    event: MessageEvent, content: Union[MessageSegment, Message, str, bytes]
) -> Message:
    """返回一个回复消息"""
    if isinstance(event, GuildMessageEvent):
        return Message(content)
    if type(content) == bytes:
        return MessageSegment.reply(event.message_id) + MessageSegment.image(content)
    if content[0:9] == "base64://":
        return MessageSegment.reply(event.message_id) + MessageSegment.image(content)
    return MessageSegment.reply(event.message_id) + content


# 生成一个由qq号和nickname共同决定的uuid作为真名，防止重名
def generate_truename(user_id, nickname) -> str:
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    s = user_id + nickname + current_time_str
    # 将字符串转换为 UUID 对象
    uuid_object = uuid.uuid3(uuid.NAMESPACE_DNS, s)
    # 获取 UUID 对象的 bytes 值
    uuid_bytes = uuid_object.bytes
    # 将 bytes 值转换为字符串
    uuid_str = uuid_bytes.hex()[:14]
    return uuid_str


def generate_random_string(length=8) -> str:
    """生成指定长度的随机字符串"""
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def is_email(email) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_useable(event, mode=poe_persistor.mode):
    if poe_persistor.poe_cookie:
        if mode == "black":
            try:
                if str(event.user_id) in poe_persistor.blacklist:
                    logger.warning(f"黑名单用户:{str(event.user_id)},跳过")
                    return False
            except:
                pass
            try:
                if str(event.group_id) in poe_persistor.blacklist:
                    logger.warning(f"黑名单群聊:{str(event.group_id)},跳过")
                    return False
            except:
                pass
            return True
        elif mode == "white":
            try:
                if str(event.user_id) in poe_persistor.whitelist:
                    return True
            except:
                pass
            try:
                if str(event.group_id) in poe_persistor.whitelist:
                    return True
            except:
                pass
            logger.warning("用户或群聊不在白名单内，跳过")
            return False
    else:
        logger.warning("没有配置poe的cookie，无法使用，跳过")
        return False


def is_vip(event):
    try:
        if str(event.user_id) in poe_persistor.accesslist:
            return True
    except:
        pass
    try:
        if str(event.group_id) in poe_persistor.accesslist:
            return True
    except:
        pass
    logger.warning("非vip用户或群聊，跳过")
    return False


async def close_page(page):
    try:
        await page.close()
    except:
        pass


async def send_msg(result, matcher, event):
    msgid_container = {}
    suggest_container = []

    async def sendmsg(msg, matcher, event):
        if poe_persistor.pic_able is not None:
            if poe_persistor.pic_able == "True":
                pic = await md_to_pic(msg)
                if poe_persistor.url_able == "True":
                    url = await get_url(msg)
                    msgid_container = await matcher.send(
                        reply_out(event, pic) + MessageSegment.text(url)
                    )
                else:
                    msgid_container = await matcher.send(reply_out(event, pic))
            else:
                msgid_container = await matcher.send(reply_out(event, msg))
        else:
            if len(msg) > poe_persistor.num_limit:
                pic = await md_to_pic(msg)
                if poe_persistor.url_able == "True":
                    url = await get_url(msg)
                    msgid_container = await matcher.send(
                        reply_out(event, pic) + MessageSegment.text(url)
                    )
                else:
                    msgid_container = await matcher.send(reply_out(event, pic))
            else:
                msgid_container = await matcher.send(reply_out(event, msg))
        return msgid_container

    if isinstance(result, tuple):
        last_answer, suggest_container = result
        is_successful = True
    elif isinstance(result, str):
        if "banned" == result:
            await matcher.send(reply_out(event, "你的机器人被banned了，请/pc新建一个机器人，并且不要在使用此预设"))
            matcher.finish()
            return msgid_container, []
        elif "limited" == result:
            await matcher.send(reply_out(event, "今日免费限额已用尽，请订阅或等明天再使用"))
            matcher.finish()
            return msgid_container, []
    elif isinstance(result, bool):
        is_successful = result
    else:
        raise ValueError("未知错误")

    if is_successful:
        if poe_persistor.suggest_able == "True" and suggest_container:
            suggest_str = "  \n".join(
                [f"{i+1}: {s}" for i, s in enumerate(suggest_container)]
            )
            msg = f"{last_answer}  \n\n建议回复：  \n{suggest_str}"
        else:
            msg = f"{last_answer}\n"

        msgid_container = await sendmsg(msg, matcher, event)
        return msgid_container, suggest_container
    else:
        await matcher.send(reply_out(event, "出错了，多次出错请联系机器人管理员"))
        return msgid_container, suggest_container
