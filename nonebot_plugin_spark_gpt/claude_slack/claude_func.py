from typing import Union
import uuid, asyncio
from nonebot import logger, require

require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from .config import claude_slack_persistor
from ..common.render.render import md_to_pic
from ..common.common_func import get_url, reply_out


def random_uuid4():
    return str(uuid.uuid4())[:8]


def is_useable(event, mode=claude_slack_persistor.mode):
    if (
        claude_slack_persistor.channel_id
        and claude_slack_persistor.claude_id
        and claude_slack_persistor.slack_user_token
    ):
        if mode == "black":
            try:
                if str(event.user_id) in claude_slack_persistor.blacklist:
                    logger.warning(f"黑名单用户:{str(event.user_id)},跳过")
                    return False
            except:
                pass
            try:
                if str(event.group_id) in claude_slack_persistor.blacklist:
                    logger.warning(f"黑名单群聊:{str(event.group_id)},跳过")
                    return False
            except:
                pass
            return True
        elif mode == "white":
            try:
                if str(event.user_id) in claude_slack_persistor.whitelist:
                    return True
            except:
                pass
            try:
                if str(event.group_id) in claude_slack_persistor.whitelist:
                    return True
            except:
                pass
            logger.warning("用户或群聊不在白名单内，跳过")
            return False
    else:
        logger.warning("没有配置Claude_slack的相关配置，无法使用，跳过")
        return False


async def sendmsg(msg, matcher, event):
    if claude_slack_persistor.pic_able is not None:
        if claude_slack_persistor.pic_able == "True":
            pic = await md_to_pic(msg)
            if claude_slack_persistor.url_able == "True":
                url = await get_url(msg)
                msgid_container = await matcher.send(
                    reply_out(event, pic) + MessageSegment.text(url)
                )
            else:
                msgid_container = await matcher.send(reply_out(event, pic))
        else:
            msgid_container = await matcher.send(reply_out(event, msg))
    else:
        if len(msg) > claude_slack_persistor.num_limit:
            pic = await md_to_pic(msg)
            if claude_slack_persistor.url_able == "True":
                url = await get_url(msg)
                msgid_container = await matcher.send(
                    reply_out(event, pic) + MessageSegment.text(url)
                )
            else:
                msgid_container = await matcher.send(reply_out(event, pic))
        else:
            msgid_container = await matcher.send(reply_out(event, msg))
    return msgid_container
