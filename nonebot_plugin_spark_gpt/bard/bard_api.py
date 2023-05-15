import json
import httpx
from urllib.parse import quote
from nonebot import logger
from .config import BotInfo
from .config import bard_persistor

class BardChat():

    def __init__(self):
        if bard_persistor.proxy:
            self.client = httpx.AsyncClient(proxies=bard_persistor.proxy)
        else:
            self.client = httpx.AsyncClient()
        self.headers = {
            "Cookie": bard_persistor.cookie,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    async def get_at_token(self):
        response = await self.client.get(
            "https://bard.google.com/?hl=en",
            timeout=30,
            headers=self.headers,
            follow_redirects=True,
        )
        at = quote(response.text.split('"SNlM0e":"')[1].split('","')[0])
        return at
    
    async def ask(self, text: str,botinfo:BotInfo):
        bard_session_id = botinfo.bard_session_id
        r = botinfo.r
        rc = botinfo.rc
        at = botinfo.at
        try:
            url = "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate"
            content = quote(text.replace('"', "'")).replace("%0A", "%5C%5Cn")
            raw_data = f"f.req=%5Bnull%2C%22%5B%5B%5C%22{content}%5C%22%5D%2Cnull%2C%5B%5C%22{bard_session_id}%5C%22%2C%5C%22{r}%5C%22%2C%5C%22{rc}%5C%22%5D%5D%22%5D&at={at}&"
            response = await self.client.post(
                url,
                timeout=30,
                headers=self.headers,
                content=raw_data,
            )
            if response.status_code != 200:
                logger.error(f"[Bard] 请求出现错误，状态码: {response.status_code}")
                logger.error(f"[Bard] {response.text}")
                raise Exception("Authentication failed")
            res = response.text.split("\n")
            for lines in res:
                if "wrb.fr" in lines:
                    data = json.loads(json.loads(lines)[0][2])
                    result = data[0][0]
                    botinfo.bard_session_id = data[1][0]
                    botinfo.r = data[1][1]  # 用于下一次请求, 这个位置是固定的
                    for check in data:
                        if not check:
                            continue
                        try:
                            for element in [element for row in check for element in row]:
                                if "rc_" in element:
                                    botinfo.rc = element
                                    break
                        except:
                            continue
                    return result, botinfo
            else:
                raise Exception("获取bard返回消息失败")
        except Exception as e:
            raise Exception(f"[Bard] 出现了些错误:{e}")
        
bardchat = BardChat()
