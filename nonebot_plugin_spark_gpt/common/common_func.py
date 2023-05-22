import asyncio
from typing import Tuple, Union
import aiohttp
from ..chatgpt_web.config import gptweb_persistor
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from ..chatgpt_web.config import gptweb_persistor

from ..claude_slack.config import claude_slack_persistor
from ..Spark_desk.config import spark_desk_persistor
from .config import Sender, UserData, UserInfo, spark_persistor, get_user_info_and_data

if spark_persistor.poe_api_mode == 0:
    from ..poe_http.config import poe_persistor
else:
    from ..poe_pw.config import poe_persistor


def is_auto_prompt(prompt_nickname):
    if prompt_nickname in [gptweb_persistor.auto_prompt, poe_persistor.auto_prompt]:
        if prompt_nickname in gptweb_persistor.auto_prompt:
            return "CharGPT_Web"
        elif prompt_nickname in poe_persistor.auto_prompt:
            return "Poe"
    else:
        return False


def set_public_info_data(
    user_data_dict: dict[UserInfo, UserData]
) -> Tuple[UserInfo, UserData]:
    """
    接受一个event和一个user_data_dict(全局的，所有用户的),在user_data_dict匹配(无则初次设置)用户的过往使用信息
    返回UserInfo和匹配后的(无则新建的)对应用户的current_user_dict结构为[UserInfo, UserData]
    """
    user_info = UserInfo(platform="qq", user_id=123456789)
    user_data = UserData(sender=Sender(user_id=123456789, user_name="public"))
    return user_info, user_data_dict.setdefault(user_info, user_data)


def get_public_info_data() -> Tuple[UserInfo, UserData]:
    """
    接受一个event和一个user_data_dict(全局的，所有用户的),在user_data_dict匹配(无则初次设置)用户的过往使用信息
    返回UserInfo和匹配后的(无则新建的)对应用户的current_user_dict结构为[UserInfo, UserData]
    """
    user_info = UserInfo(platform="qq", user_id=123456789)
    user_data = UserData(sender=Sender(user_id=123456789, user_name="public"))
    return user_info, user_data


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


async def delete_messages(bot, dict_list: list):
    await asyncio.sleep(1)
    for eachmsg in dict_list:
        await bot.delete_msg(message_id=eachmsg["message_id"])


async def get_url(text):
    """将 Markdown 文本保存到 Mozilla Pastebin，并获得 URL"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "expires": "86400",
            "format": "url",
            "lexer": "_markdown",
            "content": text,
        }
        retries = 3
        while retries > 0:
            try:
                async with session.post(
                    "https://pastebin.mozilla.org/api/", data=payload
                ) as resp:
                    resp.raise_for_status()
                    url = await resp.text()
                    url = url[0:-1]
                    return url
            except Exception as e:
                retries -= 1
                if retries == 0:
                    url = f"上传失败：{str(e)}"
                    return url
                await asyncio.sleep(1)


def get_botinfo(nickname, event):
    current_userinfo, current_userdata = get_user_info_and_data(
        event,
    )

    persistors = [
        gptweb_persistor,
        poe_persistor,
        claude_slack_persistor,
        spark_desk_persistor,
    ]
    for persistor in persistors:
        user_dict = persistor.user_dict
        if current_userinfo in user_dict and nickname in list(
            user_dict[current_userinfo]["all"].keys()
        ):
            botinfo = user_dict[current_userinfo]["all"][nickname]
            info_str = ""
            i = 1
            for key, value in botinfo.dict().items():
                if not value:
                    continue
                info_str += f"{i}. " + key + ": " + str(value) + "\n"
                i += 1
            return botinfo, info_str, persistor
    raise Exception("没有这个bot")


def is_nickname(nickname, event):
    current_userinfo, current_userdata = get_user_info_and_data(
        event,
    )
    if current_userinfo in gptweb_persistor.user_dict:
        gptweb_nicknames = list(gptweb_persistor.user_dict[current_userinfo]["all"].keys())
    else:
        gptweb_nicknames = []

    if current_userinfo in poe_persistor.user_dict:
        poe_nicknames = list(poe_persistor.user_dict[current_userinfo]["all"].keys())
    else:
        poe_nicknames = []

    if current_userinfo in claude_slack_persistor.user_dict:
        claude_slack_nicknames = list(claude_slack_persistor.user_dict[current_userinfo]["all"].keys())
    else:
        claude_slack_nicknames = []

    if current_userinfo in spark_desk_persistor.user_dict:
        spark_desk_nicknames = list(spark_desk_persistor.user_dict[current_userinfo]["all"].keys())
    else:
        spark_desk_nicknames = []

    nicknames = [gptweb_nicknames, poe_nicknames, claude_slack_nicknames, spark_desk_nicknames]
    flat_list = [item for sublist in nicknames for item in sublist]
    return nickname in flat_list


def is_public_nickname(nickname):
    public_user_info, public_user_data = get_public_info_data()
    if public_user_info in gptweb_persistor.user_dict:
        gptweb_nicknames = list(gptweb_persistor.user_dict[public_user_info]["all"].keys())
    else:
        gptweb_nicknames = []

    if public_user_info in poe_persistor.user_dict:
        poe_nicknames = list(poe_persistor.user_dict[public_user_info]["all"].keys())
    else:
        poe_nicknames = []

    if public_user_info in claude_slack_persistor.user_dict:
        claude_slack_nicknames = list(claude_slack_persistor.user_dict[public_user_info]["all"].keys())
    else:
        claude_slack_nicknames = []

    if public_user_info in spark_desk_persistor.user_dict:
        spark_desk_nicknames = list(spark_desk_persistor.user_dict[public_user_info]["all"].keys())
    else:
        spark_desk_nicknames = []

    nicknames = [gptweb_nicknames, poe_nicknames, claude_slack_nicknames, spark_desk_nicknames]
    flat_list = [item for sublist in nicknames for item in sublist]
    return nickname in flat_list


def get_public_botinfo(nickname):
    current_userinfo, current_userdata = get_public_info_data()

    persistors = [
        gptweb_persistor,
        poe_persistor,
        claude_slack_persistor,
        spark_desk_persistor,
    ]
    for persistor in persistors:
        user_dict = persistor.user_dict
        if current_userinfo in user_dict and nickname in list(
            user_dict[current_userinfo]["all"].keys()
        ):
            botinfo = user_dict[current_userinfo]["all"][nickname]
            info_str = ""
            i = 1
            for key, value in botinfo.dict().items():
                if not value:
                    continue
                info_str += f"{i}. " + key + ": " + str(value) + "\n"
                i += 1
            return botinfo, info_str, persistor
    raise Exception("没有这个bot")
