import json
from pathlib import Path
import re
from nonebot import logger
from nonebot.plugin import on_command, on_message
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Message,
    Event,
    Bot,
    MessageEvent,
    MessageSegment,
)
from .bard_func import is_useable, sendmsg
from .config import BotInfo, bard_persistor, BardTemper, set_userdata
from ..common.render.render import md_to_pic
from ..common.common_func import reply_out
from .bard_api import bardchat
sourcepath = Path(__file__).parent.parent / "source"


logger.info("开始加载Bard")
bardtemper = BardTemper()
user_data_dict = bardtemper.user_data_dict


#############################################################
async def _is_chat_(event: MessageEvent, bot: Bot):
    try:
        current_userinfo, current_userdata = set_userdata(
            event=event, user_data_dict=user_data_dict
        )
    except:
        return False
    if bool(event.reply):
        if (
            str(event.reply.sender.user_id) == bot.self_id
            and event.reply.message_id == current_userdata.last_reply_message_id
        ):
            if not is_useable(event):
                return False
            raw_message = str(event.message)
            if not raw_message:
                return False
            return raw_message, current_userinfo, current_userdata
        else:
            return False
    elif str(event.message).startswith(("/bard", "/gb")) and not str(event.message).startswith(("/bardh", "/gbh")):
        if not is_useable(event):
            return False
        raw_message = (
            str(event.message)
            .replace("/bard ", "")
            .replace("/bard", "")
            .replace("/gb ", "")
            .replace("/gb", "")
        )

        if not raw_message:
            return False
        if not current_userdata.botinfo:
            try:
                at = await bardchat.get_at_token()
                current_userdata.botinfo = BotInfo(at=at)
            except Exception as e:
                logger.error(f"Bard出错了:{e}")
                return False
        
        return raw_message, current_userinfo, current_userdata

bard_chat__ = on_message(priority=1, block=False)


@bard_chat__.handle()
async def __bard_chat____(matcher: Matcher, event: Event, bot: Bot):
    temp_tuple = await _is_chat_(event, bot)
    if temp_tuple == False or not temp_tuple:
        await matcher.finish()
    else:
        if isinstance(temp_tuple, tuple):
            raw_message, current_userinfo, current_userdata = temp_tuple
            botinfo = current_userdata.botinfo
        elif isinstance(temp_tuple, str):
            await matcher.finish(reply_out(event, f"出错了:{temp_tuple}"))
    if current_userdata.is_waiting:
        await matcher.finish(reply_out(event, "你有一个对话进行中，请等结束后再继续询问"))
        
    if raw_message in [
        "清除对话",
        "清空对话",
        "清除历史",
        "清空历史",
        "清除记录",
        "清空记录",
        "清空历史对话",
        "刷新对话",
    ]:
        
        current_userdata.botinfo.at = await bardchat.get_at_token()
        current_userdata.botinfo.bard_session_id=""
        current_userdata.botinfo.r=""
        current_userdata.botinfo.rc=""
        reply_msg = await matcher.send(reply_out(event, "成功刷新对话"))
        current_userdata.last_reply_message_id = reply_msg["message_id"]
        await matcher.finish()
    try:
        current_userdata.is_waiting = True
        wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
        result,current_userdata.botinfo = await bardchat.ask(raw_message,botinfo)
        current_userdata.is_waiting = False
    except:
        current_userdata.is_waiting = False
        await matcher.send(reply_out(event, "出错喽，多次重试都出错的话，联系机器人主人"))
        await bot.delete_msg(wait_msg["message_id"])
        await matcher.finish()
    await bot.delete_msg(message_id = wait_msg["message_id"])
    reply_msg = await sendmsg(result,matcher,event)
    current_userdata.last_reply_message_id = reply_msg["message_id"]
    await matcher.finish()

######################################################
bard_help = on_command("bardhelp", aliases={"bard帮助", "gbh"}, priority=4, block=False)


@bard_help.handle()
async def __bard_help__(matcher: Matcher):
    if not is_useable:
        await matcher.finish()
    msg = """
# spark-gpt Bard使用说明

- 机器人对每个人都是相互独立的。

- !!! 以下命令前面全部要加 '/' !!!  

## 对话命令
- 支持以下特性：可以通过对话 (清除/清空)(对话/历史)或"刷新对话"或"清空历史对话"来开启另一个新对话  
- 对话一次后，就可以直接回复机器人给你的最后的回复来进行连续对话  

| 命令 | 描述 |
| --- | --- |
| `/bard / gb + 内容` | 对话功能|

"""
    # pic = await md_to_pic(msg)
    await matcher.send(MessageSegment.image(Path(sourcepath / Path("demo(7).png")).absolute()))

    await matcher.finish()
