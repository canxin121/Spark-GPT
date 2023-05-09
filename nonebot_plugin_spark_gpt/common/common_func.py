import asyncio
from typing import Union

import aiohttp
from ..poe.config import poe_persistor
from ..chatgpt_web.config import gptweb_persistor
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment


def is_auto_prompt(prompt_nickname):
    if prompt_nickname in [gptweb_persistor.auto_prompt, poe_persistor.auto_prompt]:
        if prompt_nickname in gptweb_persistor.auto_prompt:
            return "CharGPT_Web"
        elif prompt_nickname in poe_persistor.auto_prompt:
            return "Poe"
    else:
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
