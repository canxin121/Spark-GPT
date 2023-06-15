import aiohttp
import base64
import copy
import json
from .config import spark_desk_persistor

class SparkChat:
    def __init__(self):
        self.cookie = spark_desk_persistor.cookie
        self.fd = spark_desk_persistor.fd
        self.GtToken = spark_desk_persistor.GtToken
        self.sid = spark_desk_persistor.sid
        self.headers = {
            'Accept': 'text/event-stream',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'Origin': 'https://xinghuo.xfyun.cn',
            'Referer': 'https://xinghuo.xfyun.cn/desk',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        self.chat_header = copy.copy(self.headers)
        self.chat_header['Accept'] = 'application/json, text/plain, */*'
        self.chat_header['Content-Type'] = 'application/json'
        self.chat_header['X-Requested-With'] = 'XMLHttpRequest'

    async def generate_chat_id(self):
        url = 'https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/create-chat-list'
        payload = "{}"
        async with aiohttp.ClientSession(headers=self.chat_header) as session:
            retry_count = 0
            while retry_count < 3:
                try:
                    async with session.post(url, data=payload) as response:
                        response_data = await response.json()
                        if response_data['code'] == 0:
                            chat_list_id = response_data['data']['id']
                            self.chat_id = chat_list_id
                            return chat_list_id
                        else:
                            raise Exception(f"Failed to generate chat ID. Error code: {response_data['code']}")
                except Exception as e:
                    retry_count += 1
                    if retry_count >= 3:
                        raise e


    async def set_name(self, chat_id, question):
        url = "https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/rename-chat-list"
        question = question[:15]
        payload = {
            'chatListId': chat_id,
            'chatListName': question,
        }
        async with aiohttp.ClientSession(headers=self.chat_header) as session:
            retry_count = 0
            while retry_count < 3:
                try:
                    async with session.post(url, data=json.dumps(payload)) as response:
                        response_data = await response.json()
                        if response_data['code'] == 0:
                            return True
                        else:
                            raise Exception(f"Failed to set chat name. Error code: {response_data['code']}")
                except Exception as e:
                    retry_count += 1
                    if retry_count >= 3:
                        raise Exception(f"Error setting chat name: {str(e)}.")

    def decode(self, text):
        try:
            decoded_data = base64.b64decode(text).decode('utf-8')
            return decoded_data
        except Exception as e:
            return ''

    async def ask_question(self, chat_id, question):
        url = "https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat"
        payload = {
            'fd': self.fd,
            'chatId': chat_id,
            'text': question,
            'GtToken': self.GtToken,
            'sid': self.sid,
            'clientType': '1',
            'isBot':'0'
        }
        async with aiohttp.ClientSession(headers=self.headers) as session:
            retry_count = 0
            while retry_count < 3:
                try:
                    async with session.post(url, data=payload, timeout=None) as response:
                        response_text = await response.text()
                        response_text = ''.join(self.decode(line[len("data:"):].rstrip().lstrip().encode()) for line in response_text.splitlines() if line and self.decode(line[len("data:"):].rstrip().lstrip().encode()) != 'zw').replace('\n\n', '\n')
                        return response_text
                except Exception as e:
                    retry_count += 1
                    if retry_count >= 3:
                        raise Exception(f"Error asking question: {str(e)}.")            
sparkchat = SparkChat()