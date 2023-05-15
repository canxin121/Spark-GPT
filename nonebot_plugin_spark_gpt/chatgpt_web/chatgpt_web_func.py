from typing import Union
import uuid, asyncio
from nonebot import logger, require

require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from .config import gptweb_persistor
from ..common.render.render import md_to_pic
from ..common.common_func import get_url


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


def random_uuid4():
    return str(uuid.uuid4())


def is_useable(event, mode=gptweb_persistor.mode):
    if gptweb_persistor.session_token:
        if mode == "black":
            try:
                if str(event.user_id) in gptweb_persistor.blacklist:
                    logger.warning(f"黑名单用户:{str(event.user_id)},跳过")
                    return False
            except:
                pass
            try:
                if str(event.group_id) in gptweb_persistor.blacklist:
                    logger.warning(f"黑名单群聊:{str(event.group_id)},跳过")
                    return False
            except:
                pass
            return True
        elif mode == "white":
            try:
                if str(event.user_id) in gptweb_persistor.whitelist:
                    return True
            except:
                pass
            try:
                if str(event.group_id) in gptweb_persistor.whitelist:
                    return True
            except:
                pass
            logger.warning("用户或群聊不在白名单内，跳过")
            return False
    else:
        logger.warning("没有配置gpt_web的cookie，无法使用，跳过")
        return False


async def delete_messages(bot, user_id: str, dict_list: dict):
    await asyncio.sleep(1)
    if user_id in dict_list:
        if isinstance(dict_list[user_id], list):
            for eachmsg in dict_list[user_id]:
                await bot.delete_msg(message_id=eachmsg["message_id"])
            del dict_list[user_id]
        else:
            await bot.delete_msg(message_id=dict_list[user_id]["message_id"])
    else:
        for eachmsg in dict_list:
            await bot.delete_msg(message_id=eachmsg["message_id"])
        del dict_list


async def sendmsg(msg, matcher, event):
    if gptweb_persistor.pic_able is not None:
        if gptweb_persistor.pic_able == "True":
            pic = await md_to_pic(msg)
            if gptweb_persistor.url_able == "True":
                url = await get_url(msg)
                msgid_container = await matcher.send(
                    reply_out(event, pic) + MessageSegment.text(url)
                )
            else:
                msgid_container = await matcher.send(reply_out(event, pic))
        else:
            msgid_container = await matcher.send(reply_out(event, msg))
    else:
        if len(msg) > gptweb_persistor.num_limit:
            pic = await md_to_pic(msg)
            if gptweb_persistor.url_able == "True":
                url = await get_url(msg)
                msgid_container = await matcher.send(
                    reply_out(event, pic) + MessageSegment.text(url)
                )
            else:
                msgid_container = await matcher.send(reply_out(event, pic))
        else:
            msgid_container = await matcher.send(reply_out(event, msg))
    return msgid_container
