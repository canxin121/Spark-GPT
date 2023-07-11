import ast
import asyncio
from pathlib import Path
from typing import Union

from nonebot import logger
from nonebot.adapters.discord import Message as DISCORD_Message
from nonebot.adapters.discord import MessageSegment as DISCORD_MessageSegment
from nonebot.adapters.discord.bot import Bot as DISCORD_Bot
from nonebot.adapters.discord.event import MessageEvent as DISCORD_MessageEvent
from nonebot.adapters.kaiheila import Message as KOOKMessage
from nonebot.adapters.kaiheila import MessageSegment as KOOKMessageSegment
from nonebot.adapters.kaiheila.bot import Bot as KOOKBot
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent as KOOKChannelMessageEvent,
)
from nonebot.adapters.kaiheila.event import MessageEvent as KOOKMessageEvent
from nonebot.adapters.kaiheila.event import (
    PrivateMessageEvent as KOOKPrivateMessageEvent,
)
from nonebot.adapters.onebot.v11 import Bot as OB11_BOT
from nonebot.adapters.onebot.v11 import Message as OB11_Message
from nonebot.adapters.onebot.v11 import MessageEvent as OB11_MessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as OB11_MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed as OB11_ActionFailed
from nonebot.adapters.qqguild import Message as QQGUILDMessage
from nonebot.adapters.qqguild import MessageSegment as QQGUILDMessageSegment
from nonebot.adapters.qqguild.bot import Bot as QQGUILDBot
from nonebot.adapters.qqguild.event import MessageEvent as QQGUILDMassageEvent
from nonebot.adapters.telegram import Message as TGMessage
from nonebot.adapters.telegram import MessageSegment as TGMessageSegment
from nonebot.adapters.telegram.bot import Bot as TGBot
from nonebot.adapters.telegram.event import MessageEvent as TGMessageEvent
from nonebot.adapters.telegram.exception import ActionFailed as TGActionFailed
from nonebot.adapters.telegram.exception import NetworkError as TGNetworkError
from nonebot.adapters.telegram.message import File as TGFile
from nonebot.matcher import Matcher

from .userlinks import users
from ...common.config import config
from ...common.mytypes import UserInfo, CommonUserInfo
from ...common.user_data import common_users
from ...utils.text_render import txt_to_pic
from ...utils.utils import get_url

Message_Segment = Union[
    OB11_MessageSegment,
    TGMessageSegment,
    QQGUILDMessageSegment,
    KOOKMessageSegment,
    DISCORD_MessageSegment,
]
Message = Union[
    Message_Segment,
    str,
    TGMessage,
    OB11_Message,
    QQGUILDMessage,
    KOOKMessage,
    DISCORD_Message,
]
MessageEvent = Union[
    OB11_MessageEvent,
    TGMessageEvent,
    QQGUILDMassageEvent,
    KOOKMessageEvent,
    DISCORD_MessageEvent,
]
Bot = Union[OB11_BOT, TGBot, QQGUILDBot, KOOKBot, DISCORD_Bot]


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
    try:
        superusers = ast.literal_eval(superusers)
    except:
        superusers = []
    if common_userinfo.user_id not in superusers:
        await mathcer.finish()
    else:
        return


async def get_question_chatbot(event: MessageEvent, bot: Bot, matcher: Matcher):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND
    from ..temp_bots import temp_bots

    raw_text = event.get_plaintext()
    """因为kook不支持直接在event里获取reply的msgid或者判断是不是reply，只能出此下策"""
    kook_reply_msgid = ""
    if isinstance(event, KOOKChannelMessageEvent):
        kookmsg = await bot.call_api(api="message_view", msg_id=event.msg_id)
        if kookmsg.quote:
            kook_reply_msgid = kookmsg.quote.id_
    if isinstance(event, KOOKPrivateMessageEvent):
        kookmsg = await bot.call_api(
            api="directMessage_view", chat_code=event.event.code, msg_id=event.msg_id
        )
        if kookmsg.quote:
            kook_reply_msgid = kookmsg.quote.id_

    if bool(hasattr(event, "reply") and bool(event.reply)) or bool(
        bool(hasattr(event, "reply_to_message") and event.reply_to_message)
        or kook_reply_msgid
    ):
        if (
            (
                hasattr(event, "reply")
                and hasattr(event.reply, "user_id")
                and str(event.reply.sender.user_id) == bot.self_id
            )
            or (
                hasattr(event, "reply_to_message")
                and str(event.reply_to_message.from_.id) == bot.self_id
            )
            or (hasattr(event, "mentions") and str(event.mentions[0].id) == bot.self_id)
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
                return question, chatbot, common_userinfo
            except Exception as e:
                # logger.error(str(e))
                try:
                    common_userinfo = set_public_common_userinfo(bot)
                    chatbot = temp_bots.get_bot_by_msgid(
                        common_userinfo, bot, event, kook_msgid=kook_reply_msgid
                    )
                    return question, chatbot, common_userinfo
                except:
                    await matcher.finish()
        else:
            await matcher.finish()
    else:
        if raw_text.startswith(PRIVATE_COMMAND):
            common_userinfo = set_common_userinfo(event, bot)
        elif raw_text.startswith(PUBLIC_COMMAND):
            common_userinfo = set_public_common_userinfo(bot)
        try:
            question, chatbot = temp_bots.get_bot_by_text(
                common_userinfo=common_userinfo, text=raw_text
            )
            return question, chatbot, common_userinfo
        except Exception as e:
            await matcher.finish()


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
    from ...common.load_config import PICABLE, NUMLIMIT, URLABLE, PIC_WIDTH

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
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
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
                path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
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
            try:
                return await matcher.send(
                    OB11_MessageSegment.reply(event.message_id)
                    + OB11_MessageSegment.text(content)
                )
            except OB11_ActionFailed as e:
                return await matcher.send(OB11_MessageSegment.text(content))
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        try:
                            return await matcher.send(
                                OB11_MessageSegment.reply(event.message_id)
                                + OB11_MessageSegment.image(path)
                                + OB11_MessageSegment.text(url)
                            )
                        except:
                            return await matcher.send(
                                OB11_MessageSegment.image(path)
                                + OB11_MessageSegment.text(url)
                            )
                    else:
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        try:
                            return await matcher.send(
                                OB11_MessageSegment.reply(event.message_id)
                                + OB11_MessageSegment.image(path)
                            )
                        except:
                            return await matcher.send(OB11_MessageSegment.image(path))
                else:
                    try:
                        return await matcher.send(
                            OB11_MessageSegment.reply(event.message_id) + content
                        )
                    except:
                        return await matcher.send(content)
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    try:
                        return await matcher.send(
                            OB11_MessageSegment.reply(event.message_id)
                            + OB11_MessageSegment.image(path)
                            + OB11_MessageSegment.text(url)
                        )
                    except:
                        return await matcher.send(
                            OB11_MessageSegment.image(path)
                            + OB11_MessageSegment.text(url)
                        )
                else:
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    try:
                        return await matcher.send(
                            OB11_MessageSegment.reply(event.message_id)
                            + OB11_MessageSegment.image(path)
                        )
                    except:
                        return await matcher.send(OB11_MessageSegment.image(path))
            else:
                try:
                    return await matcher.send(
                        OB11_MessageSegment.reply(event.message_id) + content
                    )
                except:
                    return await matcher.send(content)
    elif isinstance(event, KOOKMessageEvent):
        if plain:
            return await bot.send(
                event, KOOKMessageSegment.text(content), reply_sender=True
            )
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(content)
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        return await bot.send(
                            event,
                            KOOKMessage(
                                KOOKMessage(
                                    KOOKMessageSegment.image(
                                        await bot.upload_file(path)
                                    )
                                )
                                + KOOKMessage(KOOKMessageSegment.text(url))
                            ),
                            reply_sender=True,
                        )
                    else:
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        return await bot.send(
                            event,
                            KOOKMessageSegment.image(await bot.upload_file(path)),
                            reply_sender=True,
                        )
                else:
                    return await bot.send(
                        event, KOOKMessageSegment.text(content), reply_sender=True
                    )
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(content)
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    return await bot.send(
                        event,
                        KOOKMessage(
                            KOOKMessage(
                                KOOKMessageSegment.image(await bot.upload_file(path))
                            )
                            + KOOKMessage(KOOKMessageSegment.text(url))
                        ),
                        reply_sender=True,
                    )
                else:
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    return await bot.send(
                        event,
                        KOOKMessageSegment.image(await bot.upload_file(path)),
                        reply_sender=True,
                    )
            else:
                return await bot.send(
                    event, KOOKMessageSegment.text(content), reply_sender=True
                )
    elif isinstance(event, DISCORD_MessageEvent):
        if plain:
            return await send_DISCORDMessage_with_retry(
                event,
                bot,
                DISCORD_MessageSegment.text(content),
                reply_message=True,
                mention_sender=True,
            )
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(content)
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        with open(path, "rb") as f:
                            any = await send_DISCORDMessage_with_retry(
                                event,
                                bot,
                                DISCORD_MessageSegment.attachment(
                                    file="temp.jpeg", content=f.read()
                                )
                                + DISCORD_MessageSegment.text(url),
                                reply_message=True,
                                mention_sender=True,
                            )
                        return any
                    else:
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        with open(path, "rb") as f:
                            any = await send_DISCORDMessage_with_retry(
                                event,
                                bot,
                                DISCORD_MessageSegment.attachment(
                                    file="temp.jpeg", content=f.read()
                                ),
                                reply_message=True,
                                mention_sender=True,
                            )
                        return any
                else:
                    return await send_DISCORDMessage_with_retry(
                        event,
                        bot,
                        DISCORD_MessageSegment.text(content),
                        reply_message=True,
                        mention_sender=True,
                    )
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(content)
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    with open(path, "rb") as f:
                        any = await send_DISCORDMessage_with_retry(
                            event,
                            bot,
                            DISCORD_MessageSegment.attachment(
                                file="temp.jpeg", content=f.read()
                            )
                            + DISCORD_MessageSegment.text(url),
                            reply_message=True,
                            mention_sender=True,
                        )
                    return any
                else:
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    with open(path, "rb") as f:
                        any = await send_DISCORDMessage_with_retry(
                            event,
                            bot,
                            DISCORD_MessageSegment.attachment(
                                file="temp.jpeg", content=f.read()
                            ),
                            reply_message=True,
                            mention_sender=True,
                        )
                    return any
            else:
                return await send_DISCORDMessage_with_retry(
                    event,
                    bot,
                    DISCORD_MessageSegment.text(content),
                    reply_message=True,
                    mention_sender=True,
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
        return await matcher.send(OB11_MessageSegment.image(path))
    elif isinstance(event, KOOKMessageEvent):
        any = await bot.send(
            event, KOOKMessageSegment.image(await bot.upload_file(path))
        )
        return any
    elif isinstance(event, DISCORD_MessageEvent):
        with open(path, "rb") as f:
            any = await bot.send(
                event,
                DISCORD_MessageSegment.attachment(file="temp.jpeg", content=f.read()),
            )
        return any


async def send_DISCORDMessage_with_retry(
    event: DISCORD_MessageEvent, bot: DISCORD_Bot, msg, **kargs
):
    retry = 5
    while retry > 0:
        try:
            any = await bot.send(event, msg, **kargs)
            return any
        except:
            retry -= 1


async def send_message(
    content: str,
    matcher: Matcher,
    bot: Bot,
    event: MessageEvent,
    plain: bool = True,
    force_pic=False,
):
    from ...common.load_config import PIC_WIDTH, NUMLIMIT, PICABLE, URLABLE

    """跨平台回复消息"""
    if isinstance(event, TGMessageEvent):
        if force_pic:
            path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
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
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
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
                path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                any = await send_TGMessagePhoto_with_retry(path, url, bot, event)
                return any
            else:
                any = await send_TGMessageText_with_retry(content, bot, event)
                return any
    elif isinstance(event, OB11_MessageEvent):
        if force_pic:
            path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
            return await matcher.send(OB11_MessageSegment.image(path))
        if plain:
            return await matcher.send(content)
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        return await matcher.send(
                            OB11_MessageSegment.image(path)
                            + OB11_MessageSegment.text(url)
                        )
                    else:
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        return await matcher.send(OB11_MessageSegment.image(path))
                else:
                    return await matcher.send(content)
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    return await matcher.send(
                        OB11_MessageSegment.image(path) + OB11_MessageSegment.text(url)
                    )
                else:
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    return await matcher.send(OB11_MessageSegment.image(path))
            else:
                return await matcher.send(content)
    elif isinstance(event, KOOKMessageEvent):
        if force_pic:
            path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
            any = await bot.send(
                event, KOOKMessageSegment.image(await bot.upload_file(path))
            )
            return any
        if plain:
            return await bot.send(event, KOOKMessageSegment.text(content))
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(str(content))
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        return await bot.send(
                            event,
                            KOOKMessage(
                                KOOKMessage(
                                    KOOKMessageSegment.image(
                                        await bot.upload_file(path)
                                    )
                                )
                                + KOOKMessage(KOOKMessageSegment.text(url))
                            ),
                            reply_sender=True,
                        )
                    else:
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        any = await bot.send(
                            event, KOOKMessageSegment.image(await bot.upload_file(path))
                        )
                        return any
                else:
                    return await bot.send(event, KOOKMessageSegment.text(content))
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(str(content))
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    return await bot.send(
                        event,
                        KOOKMessage(
                            KOOKMessage(
                                KOOKMessageSegment.image(await bot.upload_file(path))
                            )
                            + KOOKMessage(KOOKMessageSegment.text(url))
                        ),
                        reply_sender=True,
                    )
                else:
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    any = await bot.send(
                        event, KOOKMessageSegment.image(await bot.upload_file(path))
                    )
                    return any
            else:
                return await bot.send(event, KOOKMessageSegment.text(content))
    elif isinstance(event, DISCORD_MessageEvent):
        if force_pic:
            path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
            with open(path, "rb") as f:
                any = await send_DISCORDMessage_with_retry(
                    event,
                    bot,
                    DISCORD_MessageSegment.attachment(
                        file="temp.jpeg", content=f.read()
                    ),
                )
            return any
        if plain:
            return await send_DISCORDMessage_with_retry(
                event,
                bot,
                DISCORD_MessageSegment.text(content),
            )
        else:
            if PICABLE == "Auto":
                if len(str(content)) > NUMLIMIT:
                    if URLABLE == "True":
                        url = await get_url(content)
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        with open(path, "rb") as f:
                            any = await send_DISCORDMessage_with_retry(
                                event,
                                bot,
                                DISCORD_MessageSegment.attachment(
                                    file="temp.jpeg", content=f.read()
                                )
                                + DISCORD_MessageSegment.text(url),
                            )
                        return any
                    else:
                        path = await txt_to_pic(
                            str(content), width=PIC_WIDTH, quality=100
                        )
                        with open(path, "rb") as f:
                            any = await send_DISCORDMessage_with_retry(
                                event,
                                bot,
                                DISCORD_MessageSegment.attachment(
                                    file="temp.jpeg", content=f.read()
                                ),
                            )
                        return any
                else:
                    return await send_DISCORDMessage_with_retry(
                        event,
                        bot,
                        DISCORD_MessageSegment.text(content),
                    )
            elif PICABLE == "True":
                if URLABLE == "True":
                    url = await get_url(content)
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    with open(path, "rb") as f:
                        any = await send_DISCORDMessage_with_retry(
                            event,
                            bot,
                            DISCORD_MessageSegment.attachment(
                                file="temp.jpeg", content=f.read()
                            )
                            + DISCORD_MessageSegment.text(url),
                        )
                    return any
                else:
                    path = await txt_to_pic(str(content), width=PIC_WIDTH, quality=100)
                    with open(path, "rb") as f:
                        any = await send_DISCORDMessage_with_retry(
                            event,
                            bot,
                            DISCORD_MessageSegment.attachment(
                                file="temp.jpeg", content=f.read()
                            ),
                        )
                    return any
            else:
                return await send_DISCORDMessage_with_retry(
                    event,
                    bot,
                    DISCORD_MessageSegment.text(content),
                )


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
    elif isinstance(bot, KOOKBot):
        for eachmsg in dict_list:
            try:
                if isinstance(event, KOOKChannelMessageEvent):
                    await bot.message_delete(msg_id=eachmsg.msg_id)
                else:
                    await bot.directMessage_delete(msg_id=eachmsg.msg_id)
            except:
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
                except:
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
