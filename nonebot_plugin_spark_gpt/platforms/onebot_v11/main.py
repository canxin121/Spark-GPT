import json
from pathlib import Path
from nonebot.exception import ActionFailed, NetworkError
from nonebot import logger
from nonebot.plugin import on_command, on_message
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import (
    Message,
    Event,
    Bot,
    MessageEvent,
    MessageSegment,
)
from nonebot.exception import MatcherException
from .utils import set_common_userinfo, set_userinfo, delete_messages
from ...common.user_data import common_users
from ...common.prompt_data import prompts
from .userlinks import users
from ...common.mytypes import UserInfo, CommonUserInfo

userinfo = on_command("用户信息", priority=1, block=False)


@userinfo.handle()
async def userinfo_(matcher: Matcher, event: Event, bot: Bot):
    common_userinfo = set_common_userinfo(event)
    common_user_id = common_userinfo.user_id
    common_user_key = common_users.get_key(common_userinfo)
    msg = f"通用用户名为:{common_user_id}\n用户密钥为:{common_user_key}"
    await matcher.finish(MessageSegment.text(msg))


user_relink = on_command("更改绑定", priority=1, block=False)


@user_relink.handle()
async def user_relink_(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    reply_msgs = []
    if not args:
        reply_msgs.append(await matcher.send(MessageSegment.text("请输入用户名和用户密钥,用空格分隔开")))
    else:
        matcher.set_arg("infos", args)
    state["reply_msgs"] = reply_msgs


@user_relink.got("infos")
async def user_relink__(
    matcher: Matcher,
    event: Event,
    state: T_State,
    bot: Bot,
    args: str = ArgStr("infos"),
):
    reply_msgs = state["reply_msgs"]
    infos = str(args).split(" ", 1)
    if len(infos) == 2:
        common_user_id, common_user_key = infos
    else:
        await delete_messages(bot, reply_msgs)
        await matcher.finish("你输入的信息格式有误,请重新发送命令和信息")
    common_userinfo = CommonUserInfo(user_id=common_user_id)
    if common_userinfo in list(common_users.user_dict.keys()):
        if common_users.get_key(common_userinfo) != common_user_key:
            await delete_messages(bot, reply_msgs)
            await matcher.finish("你输入的密钥错误,请重新发送指令和信息")
        else:
            userinfo = set_userinfo(event)
            users.link(userinfo, common_userinfo)
            await delete_messages(bot, reply_msgs)
            await matcher.finish("成功绑定至指定用户")
    else:
        await delete_messages(bot, reply_msgs)
        await matcher.finish("你输入的用户名不存在,请重新发送指令和信息")


all_prompts = on_command("所有预设", priority=1, block=False)


@all_prompts.handle()
async def all_prompts_(matcher: Matcher):
    await matcher.finish(MessageSegment.text(prompts.show_list()))


show_prompt = on_command("查询预设", priority=1, block=False)


@show_prompt.handle()
async def show_prompt_(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    state["replys"] = []
    if not args:
        state["replys"].append(
            await matcher.send(MessageSegment.text("请输入预设的名称,区分大小写"))
        )
    else:
        matcher.set_arg("prompt", args)


@show_prompt.got("prompt")
async def show_prompt__(
    matcher: Matcher, state: T_State, bot: Bot, args: str = ArgStr("prompt")
):
    try:
        prompt = prompts.show_prompt(str(args))
        await matcher.finish(MessageSegment.text(prompt))
    except MatcherException:
        await delete_messages(bot, state["replys"])
        raise
    except Exception as e:
        await matcher.finish(str(e))


delete_prompt = on_command("删除预设", priority=1, block=False)


@delete_prompt.handle()
async def delete_prompt_(
    matcher: Matcher, state: T_State, args: Message = CommandArg()
):
    state["replys"] = []
    if not args:
        state["replys"].append(
            await matcher.send(MessageSegment.text("请输入预设的名称,区分大小写"))
        )
    else:
        matcher.set_arg("prompt", args)


@delete_prompt.got("prompt")
async def delete_prompt__(
    matcher: Matcher, state: T_State, bot: Bot, args: str = ArgStr("prompt")
):
    try:
        prompts.delete(str(args))
        await matcher.finish(MessageSegment.text("成功删除了该预设"))
    except MatcherException:
        await delete_messages(bot, state["replys"])
        raise
    except Exception as e:
        await matcher.finish(str(e))


add_prompt = on_command("添加预设", priority=1, block=False)


@add_prompt.handle()
async def add_prompt_(matcher: Matcher, state: T_State):
    state["replys"] = []
    state["replys"].append(await matcher.send(MessageSegment.text("请输入预设的要设为的名称")))


@add_prompt.got("prompt_name")
async def add_prompt__(
    matcher: Matcher, state: T_State, bot: Bot, args: str = ArgStr("prompt_name")
):
    state["prompt_name"] = str(args)
    state["replys"].append(await matcher.send(MessageSegment.text("请输入预设的内容")))


@add_prompt.got("prompt")
async def add_prompt___(
    matcher: Matcher, state: T_State, bot: Bot, args: str = ArgStr("prompt")
):
    try:
        prompts.add(state["prompt_name"], str(args))
        await matcher.finish(MessageSegment.text("成功添加了对应的预设"))
    except MatcherException:
        await delete_messages(state["replys"])
        raise
    except Exception as e:
        await matcher.finish(str(e))
