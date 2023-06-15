import asyncio
from nonebot import require
from nonebot.adapters.onebot.v11 import Message, Event, MessageEvent, MessageSegment

require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent
from typing import Union
from ...common.mytypes import UserInfo,CommonUserInfo
from .userlinks import users
from ...common.user_data import common_users


def reply_out(
    event: MessageEvent, content: Union[MessageSegment, Message, str, bytes]
) -> Message:
    """返回一个回复消息MessageSegment"""
    if isinstance(event, GuildMessageEvent):
        return Message(content)
    if type(content) == bytes:
        return MessageSegment.reply(event.message_id) + MessageSegment.image(content)
    if content[0:9] == "base64://":
        return MessageSegment.reply(event.message_id) + MessageSegment.image(content)
    return MessageSegment.reply(event.message_id) + content


async def delete_messages(bot, dict_list: list):
    """批量撤回消息,传入List[message or message_id]"""
    await asyncio.sleep(1)
    for eachmsg in dict_list:
        await bot.delete_msg(message_id=eachmsg["message_id"])


def set_userinfo(event: Event) -> UserInfo:
    """获取qq的UserInfo"""
    return UserInfo(platform="qq", username=event.get_user_id())


def get_common_userinfo(userinfo: UserInfo) -> CommonUserInfo:
    """通过qq的UserInfo查找CommonUserInfo"""
    return users.user_links[userinfo]


def set_common_userinfo(event: Event) -> CommonUserInfo:
    """获取用户对应CommonUserInfo,如没有则新建"""
    userinfo = set_userinfo(event=event)
    try:
        common_userinfo = get_common_userinfo(userinfo)
    except:
        common_userinfo = common_users.new_user()
        users.link(userinfo, common_userinfo)
    return common_userinfo
