from pathlib import Path

from nonebot import require
from nonebot.exception import MatcherException
from nonebot.matcher import Matcher
from nonebot.params import ArgStr
from nonebot.plugin import on_message
from nonebot.typing import T_State

require("nonebot_plugin_templates")
from nonebot_plugin_templates.templates_render import colorlist_render

from .utils import get_question_chatbot
from .utils import (
    if_super_user,
    set_common_userinfo,
    set_public_common_userinfo,
    delete_messages,
    send_message, send_img,
    if_close,
    MessageEvent,
    Bot,
)
from ..temp_bots import temp_bots
from ...chatbot.load_config import get_able_source
from ...common.mytypes import BotInfo, BotData
from ...common.prefix_data import prefixes
from ...common.prompt_data import prompts
from ...common.user_data import common_users
from ...utils.utils import is_valid_string

REFRESH_KEYWORDS = [
    "清除对话",
    "清空对话",
    "清除历史",
    "清空历史",
    "清除记录",
    "清空记录",
    "清空历史对话",
    "刷新对话",
]

chat = on_message(priority=1, block=False)


@chat.handle()
async def chat_(matcher: Matcher, event: MessageEvent, bot: Bot):
    from ...common.load_config import WAIT_MSG_ABLE

    question, chatbot, common_userinfo = await get_question_chatbot(event, bot, matcher)
    reply_msgs = []
    if chatbot.lock.locked():
        msg = "这个bot还有其他请求在处理,你的回复稍后就来"
        reply_msgs.append(await send_message(msg, matcher, bot, event, reply=True))

    if len(question) < 7:
        question = question.replace(" ", "").replace("\n", "")

    if question in REFRESH_KEYWORDS:
        async with chatbot.lock:
            if WAIT_MSG_ABLE == "True":
                reply_msgs.append(
                    await send_message("正在刷新，请稍等", matcher, bot, event, reply=True)
                )
            try:
                await chatbot.refresh()
                msg = "刷新对话成功"
            except Exception as e:
                msg = str(e)

    else:
        if len(question) >= 1:
            async with chatbot.lock:
                if WAIT_MSG_ABLE == "True":
                    reply_msgs.append(
                        await send_message("正在思考，请稍等", matcher, bot, event, reply=True)
                    )

                try:
                    msg = await chatbot.ask(question=question)
                except Exception as e:
                    msg = str(e)
        else:
            msg = "你没有输入任何问题,请重新询问并在命令后或回复中加上问题"

    try:
        await delete_messages(bot, event, reply_msgs)
    except Exception:
        pass
    reply = await send_message(msg, matcher, bot, event, plain=False, reply=True)
    temp_bots.set_bot_msgid(common_userinfo, chatbot, bot, event, reply)
    await matcher.finish()


new_bot = on_message(priority=1, block=False)
Source_Msg_Path = Path(__file__).parent / "SourceMsg.jpeg"
Source_Msg_Path.touch()


@new_bot.handle()
async def new_bot_(event: MessageEvent, matcher: Matcher, bot: Bot, state: T_State):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND
    from ...chatbot.load_config import Generated_Source_Pic, get_source_pic
    raw_message = event.get_plaintext()
    if not raw_message.startswith(
            (f"{PRIVATE_COMMAND}创建bot", f"{PUBLIC_COMMAND}创建bot")
    ):
        await matcher.finish()
    if raw_message.startswith(PUBLIC_COMMAND):
        await if_super_user(event, bot, matcher)
        state["pre_command"] = PUBLIC_COMMAND
        state["common_userinfo"] = set_public_common_userinfo(bot)
    else:
        state["pre_command"] = PRIVATE_COMMAND
        state["common_userinfo"] = set_common_userinfo(event, bot)

    state["able_source_dict"], source_des_dict = get_able_source()

    state["replys"] = []
    msg = "请输入要创建的bot的来源的序号\n输入'算了'或'取消'可以结束当前操作\n可选项如下图:"

    state["replys"].append(
        await send_message(
            msg,
            matcher,
            bot,
            event,
        )
    )
    if not Generated_Source_Pic:
        pic_bytes = await colorlist_render(source_des_dict, width=700, headline="来源列表", description="",
                                           font_size=20)
        get_source_pic()
        with open(Source_Msg_Path, "wb") as f:
            f.write(pic_bytes)
    else:
        with open(Source_Msg_Path, "rb") as f:
            pic_bytes = f.read()

    state["replys"].append(
        await send_img(
            pic_bytes,
            matcher,
            bot,
            event,
        )
    )


Prompt_Msg_Path = Path(__file__).parent / "PromptMsg.jpeg"
Prompt_Msg_Path.touch()


@new_bot.got("source_index")
async def new_bot__(
        matcher: Matcher,
        event: MessageEvent,
        state: T_State,
        bot: Bot,
        args: str = ArgStr("source_index"),
):
    await if_close(event, matcher, bot, state["replys"])

    state["source_index"] = str(args).replace("\n", "")
    if state["source_index"] not in [
        str(i) for i in range(1, len(state["able_source_dict"]) + 1)
    ]:
        await send_message("没有这个索引数字,请从头开始", matcher, bot, event)
        await delete_messages(bot, event, state["replys"])
        await matcher.finish()

    if not (
            state["able_source_dict"][state["source_index"]] == "bing"
            or state["able_source_dict"][state["source_index"]] == "bard"
            or state["able_source_dict"][state["source_index"]] == "通义千问"
    ):
        prompts_dict = prompts.show_list()
        msg = '请设置这个bot的预设\n预设是每次连续对话开始时发送初始化过去的内容,清除bot的对话历史后也会重新初始化\n\n如果不使用预设,请输入"无"或"无预设"\n如果使用本地预设,请输入预设前的数字索引\n如使用自己的预设直接发送即可\n\n输入"算了"或"取消"可以结束当前操作\n本地预设列表图片将在下面发送:'
        state["replys"].append(
            await send_message(
                msg, matcher, bot, event,
            )
        )

        if not prompts.Generated:
            pic_bytes = await colorlist_render(prompts_dict, headline="预设列表", width=800,
                                               description="")
            prompts.generate_pic()
            with open(Prompt_Msg_Path, "wb") as f:
                f.write(pic_bytes)
        else:
            with open(Prompt_Msg_Path, "rb") as f:
                pic_bytes = f.read()

        state["replys"].append(
            await send_img(
                pic_bytes, matcher, bot, event,
            )
        )
    else:
        state["prompt_nickname"] = "无预设"
        state["prefix_nickname"] = "无前缀"
        matcher.set_arg("prompt", "")
        matcher.set_arg("prefix", "")


Prefix_Msg_Path = Path(__file__).parent / "PrefixMsg.jpeg"
Prefix_Msg_Path.touch()


@new_bot.got("prompt")
async def new_bot____(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("prompt"),
):
    await if_close(event, matcher, bot, state["replys"])
    prompt = str(args).replace("\n", "")
    prompt_nickname = "自定义预设"

    try:
        prompt_nickname = state["prompt_nickname"]
    except Exception:
        pass
    if prompt in ["无", "无预设"]:
        prompt = ""
        prompt_nickname = "无预设"
    elif prompt.isdigit():
        try:
            prompt_nickname, prompt = prompts.get_prompt(prompt)
        except Exception:
            await send_message("没有这个本地预设数字索引", matcher, bot, event)
            await matcher.finish()

    state["prompt_nickname"] = prompt_nickname
    state["prompt"] = prompt

    try:
        state["prefix_nickname"]
    except Exception:
        prefixes_dict = prefixes.show_list()
        msg = '请设置这个bot的前缀\n前缀是指每次对话时都在你的问题前自动添加的一些内容\n\n如果不使用前缀,请输入"无"或"无前缀"\n如果使用本地前缀,请发送前缀前的数字索引\n如果使用自己的前缀直接发送即可\n\n输入"算了"或"取消"可以结束当前操作\n本地前缀列表图片将在下面发送:'

        state["replys"].append(
            await send_message(
                msg, matcher, bot, event
            )
        )
        if not prefixes.Generated:
            pic_bytes = await colorlist_render(prefixes_dict, headline="前缀列表", width=800,
                                               description="")
            prefixes.generate_pic()
            with open(Prefix_Msg_Path, "wb") as f:
                f.write(pic_bytes)
        else:
            with open(Prefix_Msg_Path, "rb") as f:
                pic_bytes = f.read()
        state["replys"].append(
            await send_img(
                pic_bytes, matcher, bot, event
            )
        )


@new_bot.got("prefix")
async def new_bot______(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("prefix"),
):
    await if_close(event, matcher, bot, state["replys"])
    prefix_nickname = "自定义前缀"

    try:
        prefix_nickname = state["prefix_nickname"]
    except Exception:
        pass

    prefix = str(args)
    if prefix in ["无", "无前缀"]:
        prefix = ""
        prefix_nickname = "无前缀"
    elif prefix.isdigit():
        try:
            prefix_nickname, prefix = prefixes.get_prefix(prefix)
        except Exception:
            await send_message("没有这个本地前缀数字索引", matcher, bot, event)
            await matcher.finish()
    state["prefix"] = prefix
    state["prefix_nickname"] = prefix_nickname

    state["replys"].append(
        await send_message(
            "请为这个新bot设置一个独一无二的昵称\n只允许使用中文,英文,数字组成\n输入'算了'或'取消'可以结束当前操作",
            matcher,
            bot,
            event,
        )
    )


@new_bot.got("bot_nickname")
async def new_bot___(
        matcher: Matcher,
        event: MessageEvent,
        state: T_State,
        bot: Bot,
        args: str = ArgStr("bot_nickname"),
):
    await if_close(event, matcher, bot, state["replys"])

    bot_nickname = str(args).replace("\n", "").replace("\r", "").replace(" ", "")

    if not is_valid_string(bot_nickname):
        msg = "bot的名称不能包含特殊字符,只允许中文英文和数字,请重新开始"
        await send_message(msg, matcher, bot, event)
        await delete_messages(bot, event, state["replys"])
        await matcher.finish()
    else:
        prefix = state["prefix"]
        prefix_nickname = state["prefix_nickname"]
        common_userinfo = state["common_userinfo"]

        prompt_nickname = state["prompt_nickname"]
        prompt = state["prompt"]

        botinfo = BotInfo(nickname=bot_nickname, owner=common_userinfo)
        try:
            temp_bots.add_new_bot(
                common_userinfo=common_userinfo,
                botinfo=botinfo,
                botdata=BotData(
                    nickname=bot_nickname,
                    prompt_nickname=prompt_nickname,
                    prompt=prompt,
                    prefix_nickname=prefix_nickname,
                    prefix=prefix,
                    source=state["able_source_dict"][state["source_index"]],
                ),
            )
            pre_command = state["pre_command"]
            msg = f"成功添加了bot,使用命令{pre_command}{bot_nickname}加上你要询问的内容即可使用该bot"
            await send_message(msg, matcher, bot, event)
            await matcher.finish()
        except MatcherException:
            await delete_messages(bot, event, state["replys"])
            raise
        except Exception as e:
            await send_message(str(e), matcher, bot, event)
            await matcher.finish()


delete_bot = on_message(priority=1, block=False)


@delete_bot.handle()
async def delete_bot_(matcher: Matcher, event: MessageEvent, bot: Bot, state: T_State):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND

    if not event.get_plaintext().startswith(
            (f"{PRIVATE_COMMAND}删除bot", f"{PUBLIC_COMMAND}删除bot")
    ):
        await matcher.finish()
    if event.get_plaintext().startswith(PRIVATE_COMMAND):
        state["common_userinfo"] = set_common_userinfo(event, bot)
        plain_message = (
            event.get_plaintext()
            .replace(f"{PRIVATE_COMMAND}删除bot", "")
            .replace(" ", "")
        )
    else:
        await if_super_user(event, bot, matcher)
        state["common_userinfo"] = set_public_common_userinfo(bot)
        plain_message = (
            event.get_plaintext().replace(f"{PUBLIC_COMMAND}删除bot", "").replace(" ", "")
        )
    state["replys"] = []
    if not plain_message:
        msg = "请输入bot的昵称,区分大小写\n输入'取消'或'算了'可以结束当前操作"
        state["replys"].append(await send_message(msg, matcher, bot, event))

    else:
        matcher.set_arg("bot", plain_message)


@delete_bot.got("bot")
async def delete_bot__(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("bot"),
):
    await if_close(event, matcher, bot, state["replys"])
    bot_name = str(args).replace("\n", "")
    common_userinfo = state["common_userinfo"]
    try:
        common_users.delete_bot(
            common_userinfo=common_userinfo,
            botinfo=BotInfo(nickname=bot_name, owner=common_userinfo),
        )
        await send_message("成功删除了该bot", matcher, bot, event)
        await matcher.finish()
    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


delete_bot = on_message(priority=1, block=False)


@delete_bot.handle()
async def delete_bot_(matcher: Matcher, event: MessageEvent, bot: Bot, state: T_State):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND

    if not event.get_plaintext().startswith(
            (f"{PRIVATE_COMMAND}删除bot", f"{PUBLIC_COMMAND}删除bot")
    ):
        await matcher.finish()
    if event.get_plaintext().startswith(PRIVATE_COMMAND):
        state["common_userinfo"] = set_common_userinfo(event, bot)
        plain_message = (
            event.get_plaintext()
            .replace(f"{PRIVATE_COMMAND}删除bot", "")
            .replace(" ", "")
        )
    else:
        await if_super_user(event, bot, matcher)
        state["common_userinfo"] = set_public_common_userinfo(bot)
        plain_message = (
            event.get_plaintext().replace(f"{PUBLIC_COMMAND}删除bot", "").replace(" ", "")
        )
    state["replys"] = []
    if not plain_message:
        msg = "请输入bot的昵称,区分大小写\n输入'取消'或'算了'可以结束当前操作"
        state["replys"].append(await send_message(msg, matcher, bot, event))

    else:
        matcher.set_arg("bot", plain_message)


@delete_bot.got("bot")
async def delete_bot__(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("bot"),
):
    await if_close(event, matcher, bot, state["replys"])
    bot_name = str(args).replace("\n", "")
    common_userinfo = state["common_userinfo"]
    try:
        common_users.delete_bot(
            common_userinfo=common_userinfo,
            botinfo=BotInfo(nickname=bot_name, owner=common_userinfo),
        )
        await send_message("成功删除了该bot", matcher, bot, event)
        await matcher.finish()
    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


rename_bot = on_message(priority=1, block=False)


@rename_bot.handle()
async def rename_bot_(matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND

    if not event.get_plaintext().startswith(
            (f"{PUBLIC_COMMAND}改名bot", f"{PRIVATE_COMMAND}改名bot")
    ):
        await matcher.finish()

    if event.get_plaintext().startswith(PRIVATE_COMMAND):
        state["common_userinfo"] = set_common_userinfo(event=event, bot=bot)
    else:
        await if_super_user(event, bot, matcher)
        state["common_userinfo"] = set_public_common_userinfo(bot)
    msg = "请输入要更改的bot的名称\n输入'取消'或'算了'可以结束当前操作"
    state["replys"] = []
    state["replys"].append(await send_message(msg, matcher, bot, event))


@rename_bot.got("bot_name")
async def rename_bot__(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("bot_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["bot_name"] = str(args)
    state["replys"].append(
        await send_message(
            "请输入bot要改为的名字\n注意bot的名字只能由中文,英文,数字组成\n输入'取消'或'算了'可以结束当前操作",
            matcher,
            bot,
            event,
        )
    )


@rename_bot.got("new_bot_name")
async def rename_bot___(
        matcher: Matcher,
        state: T_State,
        bot: Bot,
        event: MessageEvent,
        args: str = ArgStr("new_bot_name"),
):
    await if_close(event, matcher, bot, state["replys"])
    new_botname = str(args).replace("\n", "").replace("\r", "").replace(" ", "")
    if not is_valid_string(new_botname):
        await send_message("bot名称不能包含特殊字符,请重新开始", matcher, bot, event)
        await delete_messages(bot, event, state["replys"])
        await matcher.finish()
    try:
        common_users.rename_bot(
            state["common_userinfo"], state["bot_name"], new_botname
        )
        await send_message("成功更改了对应的bot的名称", matcher, bot, event)
        await matcher.finish()

    except MatcherException:
        await delete_messages(bot, event, state["replys"])
        raise
    except Exception as e:
        await send_message(str(e), matcher, bot, event)
        await matcher.finish()


all_bots = on_message(priority=1, block=False)


@all_bots.handle()
async def all_bots_(matcher: Matcher, bot: Bot, event: MessageEvent):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND

    if not event.get_plaintext().startswith(
            (f"{PRIVATE_COMMAND}所有bot", f"{PUBLIC_COMMAND}所有bot")
    ):
        await matcher.finish()

    if event.get_plaintext().startswith(PRIVATE_COMMAND):
        pre_command = PRIVATE_COMMAND
        common_userinfo = set_common_userinfo(event=event, bot=bot)
    else:
        pre_command = PUBLIC_COMMAND
        common_userinfo = set_public_common_userinfo(bot)

    await send_message(
        common_users.show_all_bots(common_userinfo, pre_command),
        matcher,
        bot,
        event,
        plain=False,
        forcepic=True,
        width=500,
    )
    await matcher.finish()
