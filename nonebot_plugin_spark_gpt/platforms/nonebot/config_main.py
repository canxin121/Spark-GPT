import asyncio
from pathlib import Path
from typing import Annotated
from nonebot.plugin import on_command, on_message
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.exception import MatcherException
from .utils import (
    send_img,
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
)
from ...common.web.app import start_web_ui, stop_web_ui, HOST, PORT
from ...common.user_data import common_users
from ...common.prompt_data import prompts
from ...common.prefix_data import prefixs
from .userlinks import users
from ...common.mytypes import CommonUserInfo
from ...utils.text_render import txt_to_pic
from nonebot.params import CommandStart
from ...common.load_config import get_help_pic


Help_Msg_Path = Path(__file__).parent / "HelpMsg.jpeg"

help = on_command("shelp", aliases={"s帮助", "sparkhelp"}, priority=1, block=False)


@help.handle()
async def help_(
    matcher: Matcher, event: MessageEvent, bot: Bot, foo: Annotated[str, CommandStart()]
):
    from ...common.load_config import (
        PRIVATE_COMMAND,
        PUBLIC_COMMAND,
        Generated_Help_Msg_Pic,
        PIC_WIDTH,
    )

    command_start = str(foo)
    help_msg = f"""# 1.使用bot方式
## (1).使用命令:先查询可用的bot或创建新的bot,然后使用“前缀+bot名称+你所询问的内容 或 刷新指令”,这里前缀 "{PRIVATE_COMMAND}" 使用自己的bot,前缀 "{PUBLIC_COMMAND}" 使用公用的bot.
> 当询问内容为 刷新指令 也就是 "清除对话" 或 "清空对话" 或"刷新对话" 时,将清除和bot的聊天记录,即重新开始对话
### 1).私有的bot使用示例为 “{PRIVATE_COMMAND}chat 在吗?” 这里的chat就是我自己的bot,是我创建的,并且可以通过 “{PRIVATE_COMMAND}所有bot” 查询
### 2).公用的bot使用示例为 “{PUBLIC_COMMAND}chat 在吗?” 这里的chat是公用的bot,可以通过 “{PUBLIC_COMMAND}所有bot” 查询,但只有本插件管理员可以创建
### 3).清除某个bot的聊天记录的示例为 “{PRIVATE_COMMAND}chat 刷新对话”
## (2).无需命令:直接回复某个bot的最后一条消息来继续对话
> 注意公用的bot可能也在和别人对话,所以最后一条消息不一定是发给你的最后一条

# 2.以下是bot管理命令列表,这里有两种不同前缀代表不用含义
## 使用**{PRIVATE_COMMAND}**前缀表示管理自己的bot

## 使用**{PUBLIC_COMMAND}** 前缀表示管理公用用户的bot

| 命令 | 命令含义 | 命令可用用户 |
| --- | --- | --- |
| 所有bot | 查询所有的可用的bot | 所有用户可用 |
| 创建bot | 创建新的bot(可覆盖同名bot) | {PRIVATE_COMMAND}开头仅SparkGPT管理员可用,{PUBLIC_COMMAND}开头所有用户可用 |
| 改名bot | 更改bot的名称(可覆盖同名bot) | {PRIVATE_COMMAND}开头仅SparkGPT管理员可用,{PUBLIC_COMMAND}开头所有用户可用 |
| 删除bot | 删除指定bot | {PRIVATE_COMMAND}开头仅SparkGPT管理员可用,{PUBLIC_COMMAND}开头所有用户可用 |

> 来源为bing和sydneybing的bot可以通过请求内容为"creative", "创造", "balanced", "均衡", "precise", "精确"来切换到对应模式
> 来源为bing和sydneybing的bot可以通过使用索引数字来使用建议回复,比如直接回复1来使用建议回复1

# 3.以下是用户信息命令列表,所有命令前需要加上前缀{command_start}才能触发。

| 命令 | 命令含义 | 命令可用用户 |
| --- | --- | --- |
| 用户信息 | 查询当前用户的通用用户的用户名和密钥.建议私聊使用 | 所有用户可用 |
| 更改绑定 | 将当前平台账户绑定到指定通用账户,实现跨平台数据互通 | 所有用户可用 |


# 4.以下是预设管理命令列表,所有命令前需要加上前缀{command_start}才能触发。

> 预设是指在创建某个bot时,第一条发向这个bot的人格设定,并且刷新时也会一并发送

| 命令 | 命令含义 | 命令可用用户 |
| --- | --- | --- |
| 所有预设 | 给出所有预设的名称 | 所有用户可用 |
| 查询预设 | 查询指定预设的内容 | 所有用户可用 |
| 添加预设 | 添加新的预设(可覆盖同名预设) | SparkGPT管理员可用 |
| 改名预设 | 修改预设的名字(可覆盖同名预设) | SparkGPT管理员可用 |
| 删除预设 | 删除指定预设 | SparkGPT管理员可用 |

# 5.以下是前缀管理命令列表,所有命令前需要加上前缀{command_start}才能触发。

> 前缀是指创建的bot在每次对话时,都将在你的消息前面加上这个前缀,可以使bot的回复的格式和内容满足前缀要求

| 命令 | 命令含义 | 命令可用用户 |
| --- | --- | --- |
| 所有前缀 | 给出所有前缀的名称 | 所有用户可用 |
| 查询前缀 | 查询指定前缀的内容 | 所有用户可用 |
| 添加前缀 | 添加新的前缀(可覆盖同名前缀) | SparkGPT管理员可用 |
| 改名前缀 | 修改前缀的名字(可覆盖同名前缀) | SparkGPT管理员可用 |
| 删除前缀 | 删除指定前缀 | SparkGPT管理员可用 |

# 6.以下是webui管理命令列表,所有命令前需要加上前缀{command_start}才能触发

| 命令 | 命令含义 | 命令可用用户 |
| --- | --- | --- |
| 开启webui | 默认开启,打开webui,并返回webui开启的端口(管理员可用) | SparkGPT管理员可用 |
| 关闭webui | 请在使用webui后关闭(管理员可用) | SparkGPT管理员可用 |
"""
    if not Generated_Help_Msg_Pic:
        await txt_to_pic(help_msg, Help_Msg_Path, width=PIC_WIDTH, quality=100)
        get_help_pic()
    await send_img(Help_Msg_Path, matcher, bot, event)
    await matcher.finish()


start_web_ui_ = on_command("开启webui", priority=1, block=False)


@start_web_ui_.handle()
async def start_web_ui__(matcher: Matcher, event: MessageEvent, bot: Bot):
    await if_super_user(event, bot, matcher)
    await start_web_ui()
    await send_message(
        f"成功开启webui,地址为http://{HOST}:{PORT},请在使用完成后关闭,以免他人修改内容", matcher, bot, event
    )
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
        reply_msgs.append(
            await send_message(
                "请输入用户名和用户密钥,用空格分隔开\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event
            )
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
        await send_message("你输入的信息格式有误,请重新发送命令和信息", matcher, bot, event)
        await matcher.finish()
    common_userinfo = CommonUserInfo(user_id=common_user_id)
    if common_userinfo in list(common_users.user_dict.keys()):
        if common_users.get_key(common_userinfo) != common_user_key:
            await delete_messages(bot, event, reply_msgs)
            await send_message("你输入的密钥错误,请重新发送指令和信息", matcher, bot, event)
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
        await send_message("你输入的用户名不存在,请重新发送指令和信息", matcher, bot, event)
        await matcher.finish()


all_prompts = on_command("所有预设", priority=1, block=False)


@all_prompts.handle()
async def all_prompts_(bot: Bot, matcher: Matcher, event: MessageEvent):
    from ...common.load_config import SPECIALPIC_WIDTH

    path = await txt_to_pic(prompts.show_list(), width=SPECIALPIC_WIDTH)
    await send_img(path, matcher, bot, event)
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
        state["replys"].append(
            await send_message(
                "请输入预设的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event
            )
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
        state["replys"].append(
            await send_message(
                "请输入预设的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event
            )
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
    state["replys"] = []
    state["replys"].append(
        await send_message("请输入预设的要设为的名称\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
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
        await send_message("请输入预设的内容\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
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
    state["replys"].append(
        await send_message("请输入要更改的预设的名称\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
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
        await send_message("请输入预设要改为的名字\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
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
        await send_message("成功更改了对应的预设的名称", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


all_prefixs = on_command("所有前缀", priority=1, block=False)


@all_prefixs.handle()
async def all_prefixs_(bot: Bot, matcher: Matcher, event: MessageEvent):
    from ...common.load_config import SPECIALPIC_WIDTH

    path = await txt_to_pic(prefixs.show_list(), width=SPECIALPIC_WIDTH)
    await send_img(path, matcher, bot, event)
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
        state["replys"].append(
            await send_message(
                "请输入前缀的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event
            )
        )

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
        prefix = prefixs.show_prefix(str(args))
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
        state["replys"].append(
            await send_message(
                "请输入前缀的名称,区分大小写\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event
            )
        )

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
        prefixs.delete(prefix_name)
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
    state["replys"].append(
        await send_message("请输入前缀的要设为的名称\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
    )


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
    state["replys"].append(
        await send_message("请输入前缀的内容\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
    )


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
        prefixs.add(state["prefix_name"], str(args))
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
    state["replys"].append(
        await send_message("请输入要更改的前缀的名称\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
    )


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
    state["replys"].append(
        await send_message("请输入前缀要改为的名字\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
    )


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
        prefixs.rename(old_name=state["prefix_name"], new_name=str(args))
        await send_message("成功更改了对应的前缀的名称", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()
