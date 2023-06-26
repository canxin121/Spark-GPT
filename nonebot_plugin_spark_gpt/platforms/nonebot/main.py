import json
from pathlib import Path
from typing import Union
from nonebot.exception import ActionFailed, NetworkError
from nonebot import logger
from nonebot.plugin import on_command, on_message
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException


from nonebot.exception import MatcherException
from .utils import (
    set_common_userinfo,
    set_userinfo,
    delete_messages,
    set_public_common_userinfo,
    if_super_user,
    if_close,
    send_message,
    MessageEvent,
    Message,
    Bot,
    Message_Segment,
)

from ...common.web.app import start_web_ui, stop_web_ui, HOST, PORT
from ...common.user_data import common_users
from ...common.prompt_data import prompts
from .userlinks import users
from ...common.mytypes import UserInfo, CommonUserInfo, BotInfo


help = on_command("help", priority=1, block=False)


@help.handle()
async def help_(matcher: Matcher, event: MessageEvent, bot: Bot):
    help_msg = """-以下命令前加nb设定的前缀来触发-

用户信息:查询当前用户的用户名和密钥
更改绑定:将当前平台账户绑定到指定通用账户
所有预设:给出所有预设的名称
查询预设:查询指定预设的内容
-以下仅管理员可用-
开启webui:默认开启,打开webui,并返回webui开启的端口
关闭webui:请在使用webui后关闭
添加预设:添加新的预设
预设改名:修改预设的名字
删除预设:删除指定预设

-以下命令前加/为自己单独的,加.为公用的-
-只有管理员才能创建或删除公用bot-
所有bot:查询所有的可用的bot
创建bot:创建新的bot
删除bot:删除指定bot
前缀+bot名+问题:与指定bot对话

-直接回复bot给你的最后一条回复也可以继续对话而无需命令-"""
    await send_message(matcher, bot, help_msg)
    await matcher.finish()


start_web_ui_ = on_command("开启webui", priority=1, block=False)


@start_web_ui_.handle()
async def start_web_ui__(matcher: Matcher, event: MessageEvent, bot: Bot):
    await if_super_user(event, bot, matcher)
    await start_web_ui()
    await send_message(
        matcher, bot, f"成功开启webui,地址为http://{HOST}:{PORT},请在使用完成后关闭,以免他人修改内容"
    )
    await matcher.finish()


stop_web_ui___ = on_command("关闭webui", priority=1, block=False)


@stop_web_ui___.handle()
async def stop_web_ui__(matcher: Matcher, event: MessageEvent, bot: Bot):
    await if_super_user(event, bot, matcher)
    await stop_web_ui()
    await send_message(matcher, bot, "成功关闭webui")
    await matcher.finish()


userinfo = on_command("用户信息", priority=1, block=False)


@userinfo.handle()
async def userinfo_(matcher: Matcher, event: MessageEvent, bot: Bot):
    common_userinfo = set_common_userinfo(event, bot)
    common_user_id = common_userinfo.user_id
    common_user_key = common_users.get_key(common_userinfo)
    msg = f"通用用户名为:{common_user_id}\n用户密钥为:{common_user_key}"
    await send_message(matcher, bot, msg)
    await matcher.finish()


user_relink = on_command("更改绑定", priority=1, block=False)


@user_relink.handle()
async def user_relink_(
    matcher: Matcher,
    state: T_State,
    event: MessageEvent,
    bot: Bot,
    args: Message = CommandArg(),
):
    reply_msgs = []
    if not args:
        reply_msgs.append(
            await send_message(matcher, bot, "请输入用户名和用户密钥,用空格分隔开\n输入'取消'或'算了'可以结束当前操作")
        )

    else:
        matcher.set_arg("infos", args)
    state["replys"] = reply_msgs


@user_relink.got("infos")
async def user_relink__(
    matcher: Matcher,
    event: MessageEvent,
    state: T_State,
    bot: Bot,
    args: str = ArgStr("infos"),
):
    await if_close(event, matcher, bot, state["replys"])
    reply_msgs = state["replys"]
    infos = str(args).split(" ", 1)
    if len(infos) == 2:
        common_user_id, common_user_key = infos
    else:
        await delete_messages(bot, event, reply_msgs)
        await send_message(matcher, bot, "你输入的信息格式有误,请重新发送命令和信息")
        await matcher.finish()
    common_userinfo = CommonUserInfo(user_id=common_user_id)
    if common_userinfo in list(common_users.user_dict.keys()):
        if common_users.get_key(common_userinfo) != common_user_key:
            await delete_messages(bot, event, reply_msgs)
            await send_message(matcher, bot, "你输入的密钥错误,请重新发送指令和信息")
            await matcher.finish()

        else:
            userinfo = set_userinfo(event, bot)
            origin_common_userinfo = set_common_userinfo(event, bot)
            users.link(userinfo, common_userinfo)
            common_users.if_delete_user(
                common_userinfo=origin_common_userinfo, userinfo=userinfo
            )
            await delete_messages(bot, event, reply_msgs)
            await send_message(matcher, bot, "成功绑定至指定用户")
            await matcher.finish()

    else:
        await delete_messages(bot, event, reply_msgs)
        await send_message(matcher, bot, "你输入的用户名不存在,请重新发送指令和信息")
        await matcher.finish()


all_prompts = on_command("所有预设", priority=1, block=False)


@all_prompts.handle()
async def all_prompts_(bot: Bot, matcher: Matcher):
    await send_message(matcher, bot, prompts.show_list())
    await matcher.finish()


show_prompt = on_command("查询预设", priority=1, block=False)


@show_prompt.handle()
async def show_prompt_(
    matcher: Matcher,
    state: T_State,
    bot: Bot,
    args: Message = CommandArg(),
):
    state["replys"] = []
    if not args:
        state["replys"].append(
            await send_message(matcher, bot, "请输入预设的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作")
        )

    else:
        matcher.set_arg("prompt", args)


@show_prompt.got("prompt")
async def show_prompt__(
    matcher: Matcher,
    state: T_State,
    event: MessageEvent,
    bot: Bot,
    args: str = ArgStr("prompt"),
):
    await if_close(event, matcher, bot, state["replys"])
    try:
        prompt = prompts.show_prompt(str(args))
        await send_message(matcher, bot, prompt)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(matcher, bot, str(e))
        await matcher.finish()


delete_prompt = on_command("删除预设", priority=1, block=False)


@delete_prompt.handle()
async def delete_prompt_(
    matcher: Matcher,
    state: T_State,
    event: MessageEvent,
    bot: Bot,
    args: Message = CommandArg(),
):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    if not args:
        state["replys"].append(
            await send_message(matcher, bot, "请输入预设的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作")
        )

    else:
        matcher.set_arg("prompt", args)


@delete_prompt.got("prompt")
async def delete_prompt__(
    matcher: Matcher,
    event: MessageEvent,
    state: T_State,
    bot: Bot,
    args: str = ArgStr("prompt"),
):
    await if_close(event, matcher, bot, state["replys"])
    prompt_name = str(args).replace("\n", "")
    try:
        prompts.delete(prompt_name)
        await send_message(matcher, bot, "成功删除了该预设")
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(matcher, bot, str(e))
        await matcher.finish()


add_prompt = on_command("添加预设", priority=1, block=False)


@add_prompt.handle()
async def add_prompt_(matcher: Matcher, event: MessageEvent, bot: Bot, state: T_State):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    state["replys"].append(
        await send_message(matcher, bot, "请输入预设的要设为的名称\n输入'取消'或'算了'可以结束当前操作")
    )


@add_prompt.got("prompt_name")
async def add_prompt__(
    matcher: Matcher,
    state: T_State,
    bot: Bot,
    event: MessageEvent,
    args: str = ArgStr("prompt_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["prompt_name"] = str(args)
    state["replys"].append(
        await send_message(matcher, bot, "请输入预设的内容\n输入'取消'或'算了'可以结束当前操作")
    )


@add_prompt.got("prompt")
async def add_prompt___(
    matcher: Matcher,
    state: T_State,
    bot: Bot,
    event: MessageEvent,
    args: str = ArgStr("prompt"),
):
    await if_close(event, matcher, bot, state["replys"])
    try:
        prompts.add(state["prompt_name"], str(args))
        await send_message(matcher, bot, "成功添加了对应的预设")
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(matcher, bot, str(e))
        await matcher.finish()


change_prompt_name = on_command("预设改名", priority=1, block=False)


@change_prompt_name.handle()
async def change_prompt_name_(
    matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State
):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    state["replys"].append(
        await send_message(matcher, bot, "请输入要更改的预设的名称\n输入'取消'或'算了'可以结束当前操作")
    )


@change_prompt_name.got("prompt_name")
async def change_prompt_name__(
    matcher: Matcher,
    state: T_State,
    bot: Bot,
    event: MessageEvent,
    args: str = ArgStr("prompt_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["prompt_name"] = str(args)
    state["replys"].append(
        await send_message(matcher, bot, "请输入预设要改为的名字\n输入'取消'或'算了'可以结束当前操作")
    )


@change_prompt_name.got("new_prompt_name")
async def change_prompt_name___(
    matcher: Matcher,
    state: T_State,
    bot: Bot,
    event: MessageEvent,
    args: str = ArgStr("new_prompt_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    try:
        prompts.rename(old_name=state["prompt_name"], new_name=str(args))
        await send_message(matcher, bot, "成功更改了对应的预设的名称")
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(matcher, bot, str(e))
        await matcher.finish()


all_bots = on_message(priority=1, block=False)


@all_bots.handle()
async def all_bots_(matcher: Matcher, bot: Bot, event: MessageEvent):
    if not str(event.message).startswith(("/所有bot", ".所有bot")):
        await matcher.finish()

    if str(event.message).startswith("/"):
        common_userinfo = set_common_userinfo(event=event, bot=bot)
    else:
        common_userinfo = set_public_common_userinfo(bot)
    await send_message(matcher, bot, common_users.show_all_bots(common_userinfo))
    await matcher.finish()
