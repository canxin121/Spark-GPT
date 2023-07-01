import asyncio
from pathlib import Path
from nonebot import require

import ast
from typing import Union
from ...common.mytypes import UserInfo, CommonUserInfo
from .userlinks import users
from ...common.user_data import common_users
from ...common.config import config
from ...utils.text_render import txt_to_pic
from ...utils.utils import get_url
from nonebot.matcher import Matcher
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageEvent as OB11_MessageEvent
from nonebot.adapters.onebot.v11 import Bot as OB11_BOT
from nonebot.adapters.onebot.v11 import MessageSegment as OB11_MessageSegment
from nonebot.adapters.onebot.v11 import Message as OB11_Message
from nonebot.adapters.telegram import MessageSegment as TGMessageSegment
from nonebot.adapters.telegram import Message as TGMessage
from nonebot.adapters.telegram.bot import Bot as TGBot
from nonebot.adapters.telegram.event import MessageEvent as TGMessageEvent
from nonebot.adapters.telegram.exception import NetworkError as TGNetworkError
from nonebot.adapters.telegram.exception import ActionFailed as TGActionFailed
from nonebot.adapters.telegram.message import File as TGFile

Message_Segment = Union[OB11_MessageSegment, TGMessageSegment]
Message = Union[Message_Segment, str, TGMessage, OB11_Message]
MessageEvent = Union[OB11_MessageEvent, TGMessageEvent]
Bot = Union[OB11_BOT, TGBot]

PICABLE = "Auto"
NUMLIMIT = 850
URLABLE = "True"


def load_config():
    global PICABLE, NUMLIMIT, URLABLE
    try:
        PICABLE = config.get_config("总控配置", "pic_able")
    except:
        PICABLE = "Auto"

    if PICABLE == "Auto":
        try:
            NUMLIMIT = int(config.get_config("总控配置", "num_limit"))
        except:
            NUMLIMIT = 800
        try:
            URLABLE = config.get_config("总控配置", "url_able")
        except:
            URLABLE = False
    if PICABLE == "True":
        try:
            URLABLE = config.get_config("总控配置", "url_able")
        except:
            URLABLE = False


load_config()


async def if_close(
    event: MessageEvent,
    matcher: Matcher,
    bot: Bot,
    msg_dict: dict,
):
    """是否提前结束会话"""
    if str(event.message).replace("/n", "") in ["算了", "取消"]:
        await delete_messages(bot=bot, event=event, dict_list=msg_dict)
        await matcher.finish()
    else:
        return


async def if_super_user(event: MessageEvent, bot: Bot, mathcer: Matcher):
    """判断是否为superuser在请求,否则结束处理"""
    common_userinfo = set_common_userinfo(event, bot)
    superusers = config.get_config(source="总控配置", config_name="superusers")
    try:
        superusers = ast.literal_eval(superusers)
    except:
        superusers = []
    if common_userinfo.user_id not in superusers:
        await mathcer.finish()
    else:
        return


async def send_TGMessageText_with_retry(
    content: str, bot: Bot, event: MessageEvent, **kwargs
):
    retry = 10
    while retry > 0:
        try:
            any = await bot.send(event, content, **kwargs)
            return any
        except Exception as e:
            logger.error(f"Telegram适配器在发送消息时出错:{str(e)}")
            retry -= 1
            pass
    raise Exception("Telegram适配器在发送消息时出错次数超过上限")


async def send_TGMessagePhoto_with_retry(
    path: Union[str, Path], text: str, bot: Bot, event: MessageEvent, **kwargs
):
    retry = 10
    while retry > 0:
        try:
            if text:
                any = await bot.send(event, TGFile.photo(str(path)) + text, **kwargs)
            else:
                any = await bot.send(event, TGFile.photo(str(path)), **kwargs)
            return any
        except Exception as e:
            logger.error(f"Telegram适配器在发送图片消息时出错:{str(e)}")
            retry -= 1
            pass
    raise Exception("Telegram适配器在发送图片消息时出错次数超过上限")


async def reply_message(
    bot: Bot,
    matcher: Matcher,
    event: MessageEvent,
    content: str,
    plain: bool = True,
):
    """跨平台回复消息"""
    if isinstance(event, TGMessageEvent):
        if plain:
            any = await send_TGMessageText_with_retry(
                content, bot, event, reply_to_message_id=event.message_id
            )
            return any
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                    else:
                        url = ""
                    path = await txt_to_pic(str(content))
                    any = await send_TGMessagePhoto_with_retry(
                        path, url, bot, event, reply_to_message_id=event.message_id
                    )
                    return any
                else:
                    any = await send_TGMessageText_with_retry(
                        content, bot, event, reply_to_message_id=event.message_id
                    )
                    return any
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                else:
                    url = ""
                path = await txt_to_pic(str(content))
                any = await send_TGMessagePhoto_with_retry(
                    path, url, bot, event, reply_to_message_id=event.message_id
                )
                return any
            else:
                any = await send_TGMessageText_with_retry(
                    content, bot, event, reply_to_message_id=event.message_id
                )
                return any

    elif isinstance(event, OB11_MessageEvent):
        if plain:
            return await matcher.send(
                OB11_MessageSegment.reply(event.message_id) + content
            )
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                    else:
                        url = ""
                    path = await txt_to_pic(str(content))
                    return await matcher.send(
                        OB11_MessageSegment.reply(event.message_id)
                        + OB11_MessageSegment.image(path)
                        + OB11_MessageSegment.text(url)
                    )
                else:
                    return await matcher.send(
                        OB11_MessageSegment.reply(event.message_id) + content
                    )
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                else:
                    url = ""
                path = await txt_to_pic(str(content))
                return await matcher.send(
                    OB11_MessageSegment.reply(event.message_id)
                    + OB11_MessageSegment.image(path)
                    + OB11_MessageSegment.text(url)
                )
            else:
                return await matcher.send(
                    OB11_MessageSegment.reply(event.message_id) + content
                )


async def send_img(
    path: Union[str, Path],
    matcher: Matcher,
    bot: Bot,
    event: MessageEvent,
):
    if isinstance(event, TGMessageEvent):
        any = await send_TGMessagePhoto_with_retry(path, "", bot, event)
        return any
    elif isinstance(event, OB11_MessageEvent):
        return await matcher.send(+OB11_MessageSegment.image(path))


async def send_message(
    content: str,
    matcher: Matcher,
    bot: Bot,
    event: MessageEvent,
    plain: bool = True,
    force_pic=False,
):
    """跨平台回复消息"""
    if isinstance(event, TGMessageEvent):
        if force_pic:
            path = await txt_to_pic(str(content))
            any = await send_TGMessagePhoto_with_retry(path, "", bot, event)
            return any
        if plain:
            any = await send_TGMessageText_with_retry(content, bot, event)
            return any
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                    else:
                        url = ""
                    path = await txt_to_pic(str(content))
                    any = await send_TGMessagePhoto_with_retry(path, url, bot, event)
                    return any
                else:
                    any = await send_TGMessageText_with_retry(content, bot, event)
                    return any
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                else:
                    url = ""
                path = await txt_to_pic(str(content))
                any = await send_TGMessagePhoto_with_retry(path, url, bot, event)
                return any
            else:
                any = await send_TGMessageText_with_retry(content, bot, event)
                return any
    elif isinstance(event, OB11_MessageEvent):
        if force_pic:
            path = await txt_to_pic(str(content))
            return await matcher.send(+OB11_MessageSegment.image(path))
        if plain:
            return await matcher.send(content)
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                    else:
                        url = ""
                    path = await txt_to_pic(str(content))
                    return await matcher.send(
                        +OB11_MessageSegment.image(path) + OB11_MessageSegment.text(url)
                    )
                else:
                    return await matcher.send(Message)
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                else:
                    url = ""
                path = await txt_to_pic(str(content))
                return await matcher.send(
                    +OB11_MessageSegment.image(path) + OB11_MessageSegment.text(url)
                )
            else:
                return await matcher.send(Message)


async def delete_messages(bot: Bot, event: MessageEvent, dict_list: list):
    """批量撤回消息,传入List[message or message_id]"""
    await asyncio.sleep(1)
    if isinstance(bot, OB11_BOT):
        for eachmsg in dict_list:
            await bot.delete_msg(message_id=eachmsg["message_id"])
    elif isinstance(bot, TGBot):
        for eachmsg in dict_list:
            retry = 10
            while retry > 0:
                try:
                    await bot.delete_message(
                        chat_id=event.chat.id, message_id=eachmsg.message_id
                    )
                    break
                except TGNetworkError:
                    pass
                    retry -= 1
                except TGActionFailed:
                    return
        return


def set_userinfo(event: MessageEvent, bot: Bot) -> UserInfo:
    """获取对应平台的UserInfo"""
    return UserInfo(platform=bot.type, username=event.get_user_id())


def get_common_userinfo(userinfo: UserInfo) -> CommonUserInfo:
    """通过对应平台的UserInfo查找CommonUserInfo"""
    if users.user_links[userinfo] in common_users.user_dict.keys():
        return users.user_links[userinfo]
    else:
        raise Exception("没有这个common_userinfo")


def set_public_common_userinfo(bot: Bot) -> CommonUserInfo:
    userinfo = UserInfo(platform=bot.type, username="public_user")
    try:
        common_userinfo = get_common_userinfo(userinfo)
    except:
        common_userinfo = common_users.get_public_user(userinfo)
        users.link(userinfo, common_userinfo)
    return common_userinfo


def set_common_userinfo(event: MessageEvent, bot: Bot) -> CommonUserInfo:
    """获取用户对应CommonUserInfo,如没有则新建"""
    userinfo = set_userinfo(event=event, bot=bot)
    try:
        common_userinfo = get_common_userinfo(userinfo)
    except:
        common_userinfo = common_users.new_user(userinfo)
        users.link(userinfo, common_userinfo)
    return common_userinfo
