import asyncio
from pathlib import Path
from typing import Annotated

from nonebot.exception import MatcherException
from nonebot.matcher import Matcher
from nonebot.params import ArgStr, CommandArg
from nonebot.params import CommandStart
from nonebot.plugin import on_command
from nonebot.typing import T_State

from .userlinks import users
from .utils import (
    send_img,
    set_common_userinfo,
    set_userinfo,
    delete_messages,
    if_super_user,
    is_super_user,
    if_close,
    send_message,
    MessageEvent,
    Message,
    Bot,
)
from ...common.mytypes import CommonUserInfo
from ...common.prefix_data import prefixes
from ...common.prompt_data import prompts
from ...common.user_data import common_users
from ...common.web.app import start_web_ui, stop_web_ui, HOST, PORT
from ...utils.render import list_to_pic, menu_to_pic

Help_Msg_Path = Path(__file__).parent / "HelpMsg.jpeg"
Help_Msg_Path.touch()
Super_Msg_Path = Path(__file__).parent / "SuperMsg.jpeg"
Super_Msg_Path.touch()

help = on_command("shelp", aliases={"s帮助", "sparkhelp"}, priority=1, block=False)


@help.handle()
async def help_(
        matcher: Matcher, event: MessageEvent, bot: Bot, foo: Annotated[str, CommandStart()]
):
    from ...common.load_config import (
        PRIVATE_COMMAND,
        PUBLIC_COMMAND,
        Generated_Super_Msg_Pic,
        get_super_pic,
        Generated_Help_Msg_Pic,
        get_help_pic
    )
    command_start = str(foo)
    if is_super_user(event, bot):
        if not Generated_Super_Msg_Pic:
            help_dict = {
                "私有bot": {"des": "使用和管理自己独有的bot的命令,私有bot只有主人可使用,其他人无法使用", "funcs": {
                    f"{PRIVATE_COMMAND}bot名称+询问的问题": "与指定属于自己的bot对话\n(可使用'回复'某bot最后一个答案来连续和它对话)\n(可回复'清除历史','刷新对话'来清除bot的对话记忆)",
                    f"{PRIVATE_COMMAND}所有bot": "查询所有的可用的私有的bot,以获取bot名称和相关信息",
                    f"{PRIVATE_COMMAND}创建bot": "创建新的私有的bot",
                    f"{PRIVATE_COMMAND}改名bot": "更改自己的bot的名称",
                    f"{PRIVATE_COMMAND}删除bot": "删除指定自己的bot",
                }},
                "公有bot": {"des": "使用和管理公有的bot的命令", "funcs": {
                    f"{PUBLIC_COMMAND}bot名称+询问的问题": "与指定属于公共的bot对话\n(可使用'回复'某bot最后一个答案来连续和它对话)\n(可回复'清除历史','刷新对话'来清除bot的对话记忆)",
                    f"{PUBLIC_COMMAND}所有bot": "查询所有的可用的公共的bot,以获取bot名称和相关信息",
                    f"{PUBLIC_COMMAND}创建bot": "创建新的公用的bot",
                    f"{PUBLIC_COMMAND}改名bot": "更改公用的bot的名称",
                    f"{PUBLIC_COMMAND}删除bot": "删除指定公用的bot",
                }}, "预设": {"des": "查看和管理预设", "funcs": {
                    f"{command_start}所有预设": "列出所有预设的名称和缩略的内容",
                    f"{command_start}查询预设": "查询指定预设的具体详尽内容",
                    f"{command_start}添加预设": "添加新的预设",
                    f"{command_start}删除预设": "删除指定预设",
                    f"{command_start}改名预设": "修改指定预设的名字",
                }}, "前缀": {"des": "查看和管理前缀", "funcs": {
                    f"{command_start}所有前缀": "列出所有前缀的的名称和缩略的内容",
                    f"{command_start}查询前缀": "查询指定前缀的具体详尽内容",
                    f"{command_start}添加前缀": "添加新的前缀",
                    f"{command_start}删除前缀": "删除指定前缀",
                    f"{command_start}改名前缀": "修改指定前缀的名字",
                }}, "账户信息": {"des": "用来实现跨平台(qq,tg等)同账户身份,同步你的数据", "funcs": {
                    f"{command_start}用户信息": "查询当前用户的通用用户的用户名和密钥.(5秒后撤回,但建议私聊使用)",
                    f"{command_start}更改绑定": "将当前平台账户绑定到指定通用账户,实现跨平台数据互通",
                }}, "webui": {"des": "管理webui", "funcs": {
                    f"{command_start}开启webui": "默认开启,打开webui,并返回webui开启的端口(管理员可用)",
                    f"{command_start}关闭webui": "请在使用webui后关闭(管理员可用)",
                }}
            }
            pic_bytes = await menu_to_pic(help_dict, 800)
            with open(Super_Msg_Path, "wb") as f:
                f.write(pic_bytes)
            get_super_pic()
        else:
            with open(Super_Msg_Path, "rb") as f:
                pic_bytes = f.read()
        await send_img(pic_bytes, matcher, bot, event)
        await matcher.finish()
    else:
        if not Generated_Help_Msg_Pic:
            help_dict = {
                "私有bot": {"des": "使用和管理自己独有的bot的命令,私有bot只有主人可使用,其他人无法使用", "funcs": {
                    f"{PRIVATE_COMMAND}bot名称+询问的问题": "与指定属于自己的bot对话\n(可使用'回复'某bot最后一个答案来连续和它对话)\n(可回复'清除历史','刷新对话'来清除bot的对话记忆)",
                    f"{PRIVATE_COMMAND}所有bot": "查询所有的可用的私有的bot,以获取bot名称和相关信息",
                    f"{PRIVATE_COMMAND}创建bot": "创建新的私有的bot",
                    f"{PRIVATE_COMMAND}改名bot": "更改自己的bot的名称",
                    f"{PRIVATE_COMMAND}删除bot": "删除指定自己的bot",
                }},
                "公有bot": {"des": "使用公有bot的命令", "funcs": {
                    f"{PUBLIC_COMMAND}bot名称+询问的问题": "与指定属于公共的bot对话\n(可使用'回复'某bot最后一个答案来连续和它对话)\n(可回复'清除历史','刷新对话'来清除bot的对话记忆)",
                    f"{PUBLIC_COMMAND}所有bot": "查询所有的可用的公共的bot,以获取bot名称和相关信息",
                }}, "预设": {"des": "预设将在一次和bot的连续对话开始时发送给bot进行初始化,清除对话历史后也将重新初始化", "funcs": {
                    f"{command_start}所有预设": "列出所有预设的名称和缩略的内容",
                    f"{command_start}查询预设": "查询指定预设的具体详尽内容",
                }}, "前缀": {"des": "前缀在每次和bot对话时都会附带在消息前面", "funcs": {
                    f"{command_start}所有前缀": "列出所有前缀的的名称和缩略的内容",
                    f"{command_start}查询前缀": "查询指定前缀的具体详尽内容",
                }}, "账户信息": {"des": "用来实现跨平台(qq,tg等)同账户身份,同步你的数据", "funcs": {
                    f"{command_start}用户信息": "查询当前用户的通用用户的用户名和密钥.(5秒后撤回,但建议私聊使用)",
                    f"{command_start}更改绑定": "将当前平台账户绑定到指定通用账户,实现跨平台数据互通",
                }}
            }
            pic_bytes = await menu_to_pic(help_dict, 800)
            with open(Help_Msg_Path, "wb") as f:
                f.write(pic_bytes)
            get_help_pic()
        else:
            with open(Help_Msg_Path, "rb") as f:
                pic_bytes = f.read()
        await send_img(pic_bytes, matcher, bot, event)
        await matcher.finish()


start_web_ui_ = on_command("开启webui", priority=1, block=False)


@start_web_ui_.handle()
async def start_web_ui__(matcher: Matcher, event: MessageEvent, bot: Bot):
    await if_super_user(event, bot, matcher)
    await start_web_ui()
    msg = f"成功开启webui,地址为http://{HOST}:{PORT},请在使用完成后关闭,以免他人修改内容"
    await send_message(msg, matcher, bot, event)
    await matcher.finish()


stop_web_ui___ = on_command("关闭webui", priority=1, block=False)


@stop_web_ui___.handle()
async def stop_web_ui__(matcher: Matcher, event: MessageEvent, bot: Bot):
    await if_super_user(event, bot, matcher)
    await stop_web_ui()
    await send_message("成功关闭webui", matcher, bot, event)
    await matcher.finish()


userinfo = on_command("用户信息", priority=1, block=False)


@userinfo.handle()
async def userinfo_(matcher: Matcher, event: MessageEvent, bot: Bot):
    common_userinfo = set_common_userinfo(event, bot)
    common_user_id = common_userinfo.user_id
    common_user_key = common_users.get_key(common_userinfo)
    msg = f"通用用户名为:{common_user_id}\n用户密钥为:{common_user_key}\n该消息将在5秒后尝试被撤回,请及时保存"
    reply = await send_message(msg, matcher, bot, event)
    await asyncio.sleep(5)
    await delete_messages(bot, event, [reply])
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
        msg = "请输入用户名和用户密钥,用空格分隔开\n输入'取消'或'算了'可以结束当前操作"
        reply_msgs.append(await send_message(msg, matcher, bot, event))

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
        msg = "你输入的信息格式有误,请重新发送命令和信息"
        await send_message(msg, matcher, bot, event)
        await matcher.finish()
    common_userinfo = CommonUserInfo(user_id=common_user_id)
    if common_userinfo in list(common_users.user_dict.keys()):
        if common_users.get_key(common_userinfo) != common_user_key:
            await delete_messages(bot, event, reply_msgs)
            msg = "你输入的密钥错误,请重新发送指令和信息"
            await send_message(msg, matcher, bot, event)
            await matcher.finish()

        else:
            userinfo = set_userinfo(event, bot)
            origin_common_userinfo = set_common_userinfo(event, bot)
            users.link(userinfo, common_userinfo)
            common_users.if_delete_user(
                common_userinfo=origin_common_userinfo, userinfo=userinfo
            )
            await delete_messages(bot, event, reply_msgs)
            await send_message("成功绑定至指定用户", matcher, bot, event)
            await matcher.finish()

    else:
        await delete_messages(bot, event, reply_msgs)
        msg = "你输入的用户名不存在,请重新发送指令和信息"
        await send_message(msg, matcher, bot, event)
        await matcher.finish()


all_prompts = on_command("所有预设", priority=1, block=False)

Prompt_Msg_Path = Path(__file__).parent / "PromptMsg.jpeg"
Prompt_Msg_Path.touch()


@all_prompts.handle()
async def all_prompts_(bot: Bot, matcher: Matcher, event: MessageEvent):
    prompts_dict = prompts.show_list()
    if not prompts.Generated:
        pic_bytes = await list_to_pic(prompts_dict, headline="预设列表", width=800,
                                      description="下面只展示了前200个字符")
        prompts.generate_pic()
        with open(Prompt_Msg_Path, "wb") as f:
            f.write(pic_bytes)
    else:
        with open(Prompt_Msg_Path, "rb") as f:
            pic_bytes = f.read()
    await send_img(
        pic_bytes, matcher, bot, event,
    )
    await matcher.finish()


show_prompt = on_command("查询预设", priority=1, block=False)


@show_prompt.handle()
async def show_prompt_(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: Message = CommandArg(),
):
    state["replys"] = []
    if not args:
        msg = "请输入预设的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作"
        state["replys"].append(await send_message(msg, matcher, bot, event))

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
        await send_message(prompt, matcher, bot, event, plain=False)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
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
        msg = "请输入预设的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作"
        state["replys"].append(await send_message(msg, matcher, bot, event))

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
        await send_message("成功删除了该预设", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


add_prompt = on_command("添加预设", priority=1, block=False)


@add_prompt.handle()
async def add_prompt_(matcher: Matcher, event: MessageEvent, bot: Bot, state: T_State):
    await if_super_user(event, bot, matcher)
    msg = "请输入预设的要设为的名称\n输入'取消'或'算了'可以结束当前操作"
    state["replys"] = []
    state["replys"].append(await send_message(msg, matcher, bot, event))


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
    msg = "请输入预设的内容\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


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
        await send_message("成功添加了对应的预设", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


change_prompt_name = on_command("改名预设", priority=1, block=False)


@change_prompt_name.handle()
async def change_prompt_name_(
        matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State
):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    msg = "请输入要更改的预设的名称\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


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
    msg = "请输入预设要改为的名字\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


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
        await send_message("成功更改了对应的预设的名称", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


all_prefixes = on_command("所有前缀", priority=1, block=False)

Prefix_Msg_Path = Path(__file__).parent / "PrefixMsg.jpeg"
Prefix_Msg_Path.touch()


@all_prefixes.handle()
async def all_prefixes_(bot: Bot, matcher: Matcher, event: MessageEvent):
    prefixes_dict = prefixes.show_list()
    if not prefixes.Generated:
        pic_bytes = await list_to_pic(prefixes_dict, headline="前缀列表", width=800,
                                      description="下面只展示了前200个字符")
        prefixes.generate_pic()
        with open(Prefix_Msg_Path, "wb") as f:
            f.write(pic_bytes)
    else:
        with open(Prefix_Msg_Path, "rb") as f:
            pic_bytes = f.read()
    await send_img(
        pic_bytes, matcher, bot, event,
    )
    await matcher.finish()


show_prefix = on_command("查询前缀", priority=1, block=False)


@show_prefix.handle()
async def show_prefix_(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: Message = CommandArg(),
):
    state["replys"] = []
    if not args:
        msg = "请输入前缀的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作"
        state["replys"].append(await send_message(msg, matcher, bot, event))

    else:
        matcher.set_arg("prefix", args)


@show_prefix.got("prefix")
async def show_prefix__(
        matcher: Matcher,
        state: T_State,
        event: MessageEvent,
        bot: Bot,
        args: str = ArgStr("prefix"),
):
    await if_close(event, matcher, bot, state["replys"])
    try:
        prefix = prefixes.show_prefix(str(args))
        await send_message(prefix, matcher, bot, event, plain=False)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


delete_prefix = on_command("删除前缀", priority=1, block=False)


@delete_prefix.handle()
async def delete_prefix_(
        matcher: Matcher,
        state: T_State,
        event: MessageEvent,
        bot: Bot,
        args: Message = CommandArg(),
):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    if not args:
        msg = "请输入前缀的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作"
        state["replys"].append(await send_message(msg, matcher, bot, event))

    else:
        matcher.set_arg("prefix", args)


@delete_prefix.got("prefix")
async def delete_prefix__(
        matcher: Matcher,
        event: MessageEvent,
        state: T_State,
        bot: Bot,
        args: str = ArgStr("prefix"),
):
    await if_close(event, matcher, bot, state["replys"])
    prefix_name = str(args).replace("\n", "")
    try:
        prefixes.delete(prefix_name)
        await send_message("成功删除了该前缀", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


add_prefix = on_command("添加前缀", priority=1, block=False)


@add_prefix.handle()
async def add_prefix_(matcher: Matcher, event: MessageEvent, bot: Bot, state: T_State):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    msg = "请输入前缀的要设为的名称\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


@add_prefix.got("prefix_name")
async def add_prefix__(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("prefix_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["prefix_name"] = str(args)
    msg = "请输入前缀的内容\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


@add_prefix.got("prefix")
async def add_prefix___(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("prefix"),
):
    await if_close(event, matcher, bot, state["replys"])
    try:
        prefixes.add(state["prefix_name"], str(args))
        await send_message("成功添加了对应的前缀", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


change_prefix_name = on_command("改名前缀", priority=1, block=False)


@change_prefix_name.handle()
async def change_prefix_name_(
        matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State
):
    await if_super_user(event, bot, matcher)
    state["replys"] = []
    msg = "请输入要更改的前缀的名称\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


@change_prefix_name.got("prefix_name")
async def change_prefix_name__(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("prefix_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["prefix_name"] = str(args)
    msg = "请输入前缀要改为的名字\n输入'取消'或'算了'可以结束当前操作"
    state["replys"].append(await send_message(msg, matcher, bot, event))


@change_prefix_name.got("new_prefix_name")
async def change_prefix_name___(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("new_prefix_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    try:
        prefixes.rename(old_name=state["prefix_name"], new_name=str(args))
        await send_message("成功更改了对应的前缀的名称", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()
