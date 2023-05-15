import re
from .config import newbing_persistor
from nonebot import logger
from typing import Union
from nonebot import logger, require

require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from ..common.render.render import md_to_pic
from ..common.common_func import get_url


def is_useable(event, mode=newbing_persistor.mode):
    if mode == "black":
        try:
            if str(event.user_id) in newbing_persistor.blacklist:
                logger.warning(f"黑名单用户:{str(event.user_id)},跳过")
                return False
        except:
            pass
        try:
            if str(event.group_id) in newbing_persistor.blacklist:
                logger.warning(f"黑名单群聊:{str(event.group_id)},跳过")
                return False
        except:
            pass
        return True
    elif mode == "white":
        try:
            if str(event.user_id) in newbing_persistor.whitelist:
                return True
        except:
            pass
        try:
            if str(event.group_id) in newbing_persistor.whitelist:
                return True
        except:
            pass
        logger.warning("用户或群聊不在白名单内，跳过")
        return False


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


async def sendmsg(msg, matcher, event):
    if newbing_persistor.pic_able is not None:
        if newbing_persistor.pic_able == "True":
            pic = await md_to_pic(msg)
            if newbing_persistor.url_able == "True":
                url = await get_url(msg)
                msgid_container = await matcher.send(
                    reply_out(event, pic) + MessageSegment.text(url)
                )
            else:
                msgid_container = await matcher.send(reply_out(event, pic))
        else:
            msgid_container = await matcher.send(reply_out(event, msg))
    else:
        if len(msg) > newbing_persistor.num_limit:
            pic = await md_to_pic(msg)
            if newbing_persistor.url_able == "True":
                url = await get_url(msg)
                msgid_container = await matcher.send(
                    reply_out(event, pic) + MessageSegment.text(url)
                )
            else:
                msgid_container = await matcher.send(reply_out(event, pic))
        else:
            msgid_container = await matcher.send(reply_out(event, msg))
    return msgid_container
