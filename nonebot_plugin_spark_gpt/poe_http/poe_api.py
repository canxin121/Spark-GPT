import asyncio
import time
from .config import poe_persistor
from nonebot import logger
from concurrent.futures import ThreadPoolExecutor
import poe

client = None
def re_client():
    global client
    if poe_persistor.poe_cookie:
        retry_count = 0
        while retry_count < 2:
            try:
                temp_client = poe.Client(poe_persistor.poe_cookie)
                client = temp_client
                return "重新加载poe成功"
            except:
                retry_count += 1
                logger.warning("加载poe失败,正在尝试重试...")
        if retry_count >= 2:
            return "重新加载失败，请重试"

re_client()

last_use_time = time.time()


def poe_chat(truename, message):
    global last_use_time
    if time.time() - last_use_time > 3600 and last_use_time :
        logger.info("超时自动刷新poe client")
        re_client()
        
    try:
        result = client.send_message(truename,message,timeout=60)
        for chunk in result:
            pass
        last_use_time = time.time()
        return chunk["text"]
    except Exception as e:
        logger.error(f"出错了:{e}")
        raise Exception(f"Poe出错了:{e}")

def poe_create(truename, prompt, model_index):
    global last_use_time
    if time.time() - last_use_time > 3600 and last_use_time :
        re_client()
    if model_index == "1":
        base_model = "chinchilla"
    else:
        base_model = "a2"
    try:
        last_use_time = time.time()
        client.create_bot(truename,prompt,base_model=base_model,suggested_replies=True,linkification=True)
        return True
    except Exception as e:
        logger.error(f"出错了:{e}")
        raise Exception(f"出错了:{e}")

def poe_clear(truename):
    global last_use_time
    if time.time() - last_use_time > 3600 and last_use_time :
        re_client()
    try:
        last_use_time = time.time()
        client.send_chat_break(truename)
        return True
    except Exception as e:
        logger.error(f"出错了:{e}")
        raise Exception(f"出错了:{e}")

def poe_change(prompt,botinfo):
    global last_use_time
    if time.time() - last_use_time > 3600 and last_use_time:
        re_client()
    try:
        last_use_time = time.time()
        if botinfo.model == "gpt3.5":
            base_model = "chinchilla"
        else:
            base_model = "a2"
        truename = botinfo.truename
        botid = client.bots[truename]["defaultBotObject"]["botId"]
        client.edit_bot(botid,truename,prompt=prompt,base_model=base_model,suggested_replies=True,linkification=True)
    except Exception as e:
        logger.error(f"出错了:{e}")
        raise Exception(f"出错了:{e}")