import httpx
from urllib.parse import quote
from nonebot.log import logger
import json
from ..common.config import config
from ..common.user_data import common_users
from ..common.mytypes import BotData, BotInfo, CommonUserInfo

COOKIE = ""
PROXY = ""
ABLE = True


def load_config():
    global COOKIE, PROXY,ABLE
    ABLE = True
    try:
        PROXY = config.get_config(source="Bard配置", config_name="proxy")
    except Exception as e:
        logger.warning(f"加载Bard配置时warn:{str(e)},如果你已经配置了分流或全局代理,请无视此warn")

    try:
        COOKIE = config.get_config(source="Bard配置", config_name="cookie")
    except Exception as e:
        ABLE = False
        logger.warning(f"加载Bard配置时warn:{str(e)},无法使用Bard")


load_config()

HEADER = {
    "Cookie": COOKIE,
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
}
if PROXY:
    CLIENT = httpx.AsyncClient(proxies=PROXY)
else:
    CLIENT = httpx.AsyncClient()


class Bard_Bot:
    def __init__(
        self, common_userinfo: CommonUserInfo, bot_info: BotInfo, bot_data: BotData
    ):
        self.is_waiting = False
        self.common_userinfo = common_userinfo
        self.nickname = bot_info.nickname
        self.botdata = bot_data
        if not COOKIE:
            raise Exception("Bard的配置cookie没有填写,无法使用")

        self.client = CLIENT

    def __hash__(self) -> int:
        return hash(self.nickname)

    async def refresh(self):
        self.botdata.bard_r = ""
        self.botdata.bard_rc = ""
        self.is_waiting = True
        try:
            await self.new_at_token()
            self.is_waiting = False
            return
        except Exception as e:
            self.is_waiting = False
            raise e

    async def ask(self, question: str):
        if not self.botdata.bard_at:
            try:
                self.is_waiting = True
                await self.new_at_token()
            except Exception as e:
                self.is_waiting = False
                raise e
        try:
            self.is_waiting = True
            answer = await self.talk(question)
            self.is_waiting = False
            return answer
        except Exception as e:
            self.is_waiting = False
            raise e

    async def new_at_token(self):
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                response = await self.client.get(
                    "https://bard.google.com/?hl=en",
                    timeout=30,
                    headers=HEADER,
                    follow_redirects=True,
                )
                self.botdata.bard_at = quote(
                    response.text.split('"SNlM0e":"')[1].split('","')[0]
                )
                common_users.save_userdata(common_userinfo=self.common_userinfo)
                return
            except Exception as e:
                retry -= 3
                detail_error = str(e)
                logger.error(f"Bard在生成attoken时出错:{detail_error}")
        error = f"Bard在生成attoken时出错次数超过上限:{detail_error}"
        logger.error(error)
        raise Exception(error)

    async def talk(self, question: str):
        if not self.botdata.bard_r:
            self.botdata.bard_r = ""
        if not self.botdata.bard_rc:
            self.botdata.bard_rc = ""
        if not self.botdata.session_id:
            self.botdata.session_id = ""
        retry = 3
        detail_error = "未知错误"
        while retry > 0:
            try:
                url = "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate"
                content = quote(question.replace('"', "'")).replace("%0A", "%5C%5Cn")
                raw_data = f"f.req=%5Bnull%2C%22%5B%5B%5C%22{content}%5C%22%5D%2Cnull%2C%5B%5C%22{self.botdata.session_id}%5C%22%2C%5C%22{self.botdata.bard_r}%5C%22%2C%5C%22{self.botdata.bard_rc}%5C%22%5D%5D%22%5D&at={self.botdata.bard_at}&"
                response = await self.client.post(
                    url,
                    timeout=30,
                    headers=HEADER,
                    content=raw_data,
                )
                if response.status_code != 200:
                    detail_error = "Authentication failed"
                    raise Exception(
                        f"Bard在请求时出现错误:Authentication failed,状态码: {response.status_code},错误信息:{response.text}"
                    )
                res = response.text.split("\n")
                for lines in res:
                    if "wrb.fr" in lines:
                        data = json.loads(json.loads(lines)[0][2])
                        answer = data[0][0]
                        self.botdata.session_id = data[1][0]
                        self.botdata.bard_r = data[1][1]  # 用于下一次请求, 这个位置是固定的
                        for check in data:
                            if not check:
                                continue
                            try:
                                for element in [
                                    element for row in check for element in row
                                ]:
                                    if "rc_" in element:
                                        self.botdata.bard_rc = element
                                        break
                            except:
                                continue
                        common_users.save_userdata(common_userinfo=self.common_userinfo)
                        return answer
                else:
                    detail_error = "解析回答时缺少所需项"
                    raise Exception("解析回答时缺少所需项")
            except:
                raise Exception(f"Bard在询问时出错:{detail_error}")
        raise Exception(f"Bard在询问时错误次数超过上限:{detail_error}")
