import asyncio
import uuid
import time

import aiohttp


def generate_uuid():
    return str(uuid.uuid4()).replace("-", "")[0:10]


async def get_url(text):
    """将 Markdown 文本保存到 Mozilla Pastebin,并获得 URL"""
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
