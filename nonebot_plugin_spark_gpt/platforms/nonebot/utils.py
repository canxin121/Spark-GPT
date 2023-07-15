import ast
import asyncio
from typing import Optional, Union

from nonebot import logger
from nonebot.adapters.discord import Message as DISCORD_Message
from nonebot.adapters.discord import MessageSegment as DISCORD_MessageSegment
from nonebot.adapters.discord.bot import Bot as DISCORD_Bot
from nonebot.adapters.discord.event import MessageEvent as DISCORD_MessageEvent
from nonebot.adapters.kaiheila import Message as KOOKMessage
from nonebot.adapters.kaiheila import MessageSegment as KOOKMessageSegment
from nonebot.adapters.kaiheila.bot import Bot as KOOK_Bot
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent as KOOKChannelMessageEvent,
)
from nonebot.adapters.kaiheila.event import MessageEvent as KOOKMessageEvent
from nonebot.adapters.kaiheila.event import (
    PrivateMessageEvent as KOOKPrivateMessageEvent,
)
from nonebot.adapters.onebot.v11 import Bot as OB11_Bot
from nonebot.adapters.onebot.v11 import Message as OB11_Message
from nonebot.adapters.onebot.v11 import MessageEvent as OB11_MessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as OB11_MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed as OB11_ActionFailed
from nonebot.adapters.telegram import Message as TGMessage
from nonebot.adapters.telegram import MessageSegment as TGMessageSegment
from nonebot.adapters.telegram.bot import Bot as TG_Bot
from nonebot.adapters.telegram.event import MessageEvent as TGMessageEvent
from nonebot.adapters.telegram.exception import ActionFailed as TGActionFailed
from nonebot.adapters.telegram.exception import NetworkError as TGNetworkError
from nonebot.adapters.telegram.message import File as TGFile
from nonebot.matcher import Matcher

from .userlinks import users
from ...common.config import config
from ...common.mytypes import UserInfo, CommonUserInfo
from ...common.user_data import common_users
from ...utils.render import md_to_pic
from ...utils.utils import get_url

Message_Segment = Union[
    OB11_MessageSegment,
    TGMessageSegment,
    KOOKMessageSegment,
    DISCORD_MessageSegment,
]
Message = Union[
    Message_Segment,
    str,
    TGMessage,
    OB11_Message,
    KOOKMessage,
    DISCORD_Message,
]
MessageEvent = Union[
    OB11_MessageEvent,
    TGMessageEvent,
    KOOKMessageEvent,
    DISCORD_MessageEvent,
]
Bot = Union[OB11_Bot, TG_Bot, KOOK_Bot, DISCORD_Bot]


async def if_close(
        event: MessageEvent,
        matcher: Matcher,
        bot: Bot,
        msg_dict: list,
):
    """是否提前结束会话"""
    if event.get_plaintext().replace("/n", "") in ["算了", "取消"]:
        await delete_messages(bot, event, msg_dict)
        await matcher.finish()
    else:
        return


async def if_super_user(event: MessageEvent, bot: Bot, mathcer: Matcher):
    """判断是否为superuser在请求,否则结束处理"""
    common_userinfo = set_common_userinfo(event, bot)
    superusers = config.get_config(source="总控配置", config_name="superusers")
    if common_userinfo.user_id not in superusers:
        await mathcer.finish()
    else:
        return


def is_super_user(event: MessageEvent, bot: Bot) -> bool:
    """判断是否为superuser在请求,返回bool"""
    common_userinfo = set_common_userinfo(event, bot)
    superusers = config.get_config(source="总控配置", config_name="superusers")
    return common_userinfo.user_id in superusers



async def get_question_chatbot(event: MessageEvent, bot: Bot, matcher: Matcher):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND
    from ..temp_bots import temp_bots

    raw_text = event.get_plaintext()

    kook_reply_msgid = ""
    if isinstance(event, (KOOKChannelMessageEvent, KOOKPrivateMessageEvent)):
        kookmsg = await bot.call_api(
            api="message_view"
            if isinstance(event, KOOKChannelMessageEvent)
            else "directMessage_view",
            msg_id=event.msg_id,
            **(
                {"chat_code": event.event.code}
                if isinstance(event, KOOKPrivateMessageEvent)
                else {}
            ),
        )
        if kookmsg.quote:
            kook_reply_msgid = kookmsg.quote.id_

    reply_user_id = None
    if hasattr(event, "reply") and hasattr(event.reply, "sender"):
        reply_user_id = str(event.reply.sender.user_id)
    elif hasattr(event, "reply_to_message") and hasattr(event.reply_to_message, "from_"):
        reply_user_id = str(event.reply_to_message.from_.id)
    elif hasattr(event, "mentions"):
        reply_user_id = str(event.mentions[0].id)

    if (
            reply_user_id == bot.self_id
            or (
            kook_reply_msgid
            and event.event.mention
            and event.event.mention[0] == bot.self_id
    )
            or (
            kook_reply_msgid
            and hasattr(event, "target_id")
            and event.target_id == bot.self_id
    )
    ):
        question = raw_text
        try:
            common_userinfo = set_common_userinfo(event, bot)
            chatbot = temp_bots.get_bot_by_msgid(
                common_userinfo, bot, event, kook_msgid=kook_reply_msgid
            )
        except Exception:
            try:
                common_userinfo = set_public_common_userinfo(bot)
                chatbot = temp_bots.get_bot_by_msgid(
                    common_userinfo, bot, event, kook_msgid=kook_reply_msgid
                )
            except Exception:
                await matcher.finish()
    elif raw_text.startswith((PRIVATE_COMMAND, PUBLIC_COMMAND)):
        common_userinfo = (
            set_common_userinfo(event, bot)
            if raw_text.startswith(PRIVATE_COMMAND)
            else set_public_common_userinfo(bot)
        )
        try:
            question, chatbot = temp_bots.get_bot_by_text(
                common_userinfo=common_userinfo, text=raw_text
            )
        except Exception:
            await matcher.finish()
    else:
        await matcher.finish()

    return question, chatbot, common_userinfo


async def send_TGMessage_with_retry(bot: Bot, event: MessageEvent, *args, **kwargs):
    retry = 10
    while retry > 0:
        try:
            any = await bot.send(event, *args, **kwargs)
            return any
        except Exception as e:
            logger.error(f"Telegram适配器在发送消息时出错:{str(e)}")
            retry -= 1
            pass
    raise Exception("Telegram适配器在发送消息时出错次数超过上限")


async def send_DISCORDMessage_with_retry(
        event: DISCORD_MessageEvent, bot: DISCORD_Bot, msg, **kargs
):
    retry = 5
    while retry > 0:
        try:
            any = await bot.send(event, msg, **kargs)
            return any
        except Exception:
            retry -= 1


async def send_text(
        bot: Bot, matcher: Matcher, event: MessageEvent, content: str, reply: bool = False
):
    if isinstance(event, TGMessageEvent):
        reply_to_message_id = event.message_id if reply else None
        return await send_TGMessage_with_retry(
            bot, event, content, reply_to_message_id=reply_to_message_id
        )
    elif isinstance(event, OB11_MessageEvent):
        try:
            message = (
                OB11_MessageSegment.reply(event.message_id)
                + OB11_MessageSegment.text(content)
                if reply
                else OB11_MessageSegment.text(content)
            )
            return await matcher.send(message)
        except OB11_ActionFailed:
            return await matcher.send(OB11_MessageSegment.text(content))
    elif isinstance(event, KOOKMessageEvent):
        return await bot.send(
            event, KOOKMessageSegment.text(content), reply_sender=reply
        )
    elif isinstance(event, DISCORD_MessageEvent):
        return await send_DISCORDMessage_with_retry(
            event,
            bot,
            DISCORD_MessageSegment.text(content),
            reply_message=reply,
            mention_sender=reply,
        )


async def send_img(
        pic_bytes: bytes,
        matcher: Matcher,
        bot: Bot,
        event: MessageEvent,
        reply: bool = False,
):
    if isinstance(event, TGMessageEvent):
        reply_to_message_id = event.message_id if reply else None
        return await send_TGMessage_with_retry(
            bot,
            event,
            TGFile.photo(pic_bytes),
            reply_to_message_id=reply_to_message_id,
        )
    elif isinstance(event, OB11_MessageEvent):
        try:
            message = (
                OB11_MessageSegment.reply(event.message_id)
                + OB11_MessageSegment.image(pic_bytes)
                if reply
                else OB11_MessageSegment.image(pic_bytes)
            )
            return await matcher.send(message)
        except Exception:
            return await matcher.send(OB11_MessageSegment.image(pic_bytes))
    elif isinstance(event, KOOKMessageEvent):
        return await bot.send(
            event,
            KOOKMessage(
                KOOKMessage(KOOKMessageSegment.image(await bot.upload_file(pic_bytes)))
            ),
            reply_sender=reply,
        )
    elif isinstance(event, DISCORD_MessageEvent):
        return await send_DISCORDMessage_with_retry(
            event,
            bot,
            DISCORD_MessageSegment.attachment(file="temp.jpeg", content=pic_bytes),
            reply_message=reply,
            mention_sender=reply,
        )


async def send_img_url(
        bot: Bot,
        matcher: Matcher,
        event: MessageEvent,
        pic_bytes: bytes,
        url: str,
        reply: bool = False,
):
    if isinstance(event, TGMessageEvent):
        reply_to_message_id = event.message_id if reply else None
        return await send_TGMessage_with_retry(
            bot,
            event,
            TGFile.photo(pic_bytes) + url,
            reply_to_message_id=reply_to_message_id,
        )
    elif isinstance(event, OB11_MessageEvent):
        message = (
            (
                    OB11_MessageSegment.reply(event.message_id)
                    + OB11_MessageSegment.image(pic_bytes)
                    + OB11_MessageSegment.text(url)
            )
            if reply
            else OB11_MessageSegment.image(pic_bytes) + OB11_MessageSegment.text(url)
        )
        try:
            return await matcher.send(message)
        except Exception:
            return await matcher.send(
                OB11_MessageSegment.image(pic_bytes) + OB11_MessageSegment.text(url)
            )
    elif isinstance(event, KOOKMessageEvent):
        return await bot.send(
            event,
            KOOKMessage(
                KOOKMessage(KOOKMessageSegment.image(await bot.upload_file(pic_bytes)))
                + KOOKMessage(KOOKMessageSegment.text(url))
            ),
            reply_sender=reply,
        )
    elif isinstance(event, DISCORD_MessageEvent):
        return await send_DISCORDMessage_with_retry(
            event,
            bot,
            DISCORD_MessageSegment.attachment(file="temp.jpeg", content=pic_bytes)
            + DISCORD_MessageSegment.text(url),
            reply_message=reply,
            mention_sender=reply,
        )


async def send_message(
        content: str,
        matcher: Matcher,
        bot: Bot,
        event: MessageEvent,
        width: Optional[int] = None,
        reply: bool = False,
        plain: bool = True,
        forcepic: bool = False,
):
    """跨平台的发送消息,并可文转图"""
    from ...common.load_config import PICABLE, NUMLIMIT, URLABLE, PIC_WIDTH

    if width is not None:
        pic_width = width
    else:
        pic_width = PIC_WIDTH

    if plain:
        return await send_text(bot, matcher, event, content, reply)
    elif forcepic:
        pic_bytes = await md_to_pic(str(content), width=pic_width)
        return await send_img(pic_bytes, matcher, bot, event, reply)
    elif (PICABLE == "Auto" and len(str(content)) > NUMLIMIT) or PICABLE == "True":
        if URLABLE == "True":
            pic_bytes, url = await asyncio.gather(
                md_to_pic(content, width=pic_width), get_url(content)
            )
            return await send_img_url(bot, matcher, event, pic_bytes, url, reply)
        else:
            pic_bytes = await md_to_pic(str(content), width=pic_width)
            return await send_img(pic_bytes, matcher, bot, event, reply)
    else:
        return await send_text(bot, matcher, event, content, reply)


async def delete_messages(bot: Bot, event: MessageEvent, dict_list: list):
    """批量撤回消息,传入List[message or message_id]"""
    if isinstance(bot, OB11_Bot):
        for eachmsg in dict_list:
            await bot.delete_msg(message_id=eachmsg["message_id"])
    elif isinstance(bot, TG_Bot):
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
    elif isinstance(bot, KOOK_Bot):
        for eachmsg in dict_list:
            try:
                if isinstance(event, KOOKChannelMessageEvent):
                    await bot.message_delete(msg_id=eachmsg.msg_id)
                else:
                    await bot.directMessage_delete(msg_id=eachmsg.msg_id)
            except Exception:
                pass
    elif isinstance(bot, DISCORD_Bot):
        for eachmsg in dict_list:
            retry = 3
            while retry > 0:
                try:
                    await bot.call_api(
                        "delete_message",
                        channel_id=eachmsg.channel_id,
                        message_id=eachmsg.id,
                    )
                    break
                except Exception:
                    retry -= 1
                    pass


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
    except Exception:
        common_userinfo = common_users.get_public_user(userinfo)
        users.link(userinfo, common_userinfo)
    return common_userinfo


def set_common_userinfo(event: MessageEvent, bot: Bot) -> CommonUserInfo:
    """获取用户对应CommonUserInfo,如没有则新建"""
    userinfo = set_userinfo(event=event, bot=bot)
    try:
        common_userinfo = get_common_userinfo(userinfo)
    except Exception:
        common_userinfo = common_users.new_user(userinfo)
        users.link(userinfo, common_userinfo)
    return common_userinfo
