from nonebot.exception import MatcherException
from nonebot.matcher import Matcher
from nonebot.params import ArgStr
from nonebot.plugin import on_message
from nonebot.typing import T_State
from ...utils.utils import is_valid_string
from .utils import (
    if_super_user,
    set_common_userinfo,
    set_public_common_userinfo,
    delete_messages,
    send_message,
    if_close,
    reply_message,
    MessageEvent,
    Bot,
    txt_to_pic,
    send_img,
)
from ..temp_bots import temp_bots
from ...chatbot.load_config import get_able_source
from ...common.mytypes import BotInfo, BotData
from ...common.prompt_data import prompts
from ...common.user_data import common_users
from .utils import get_question_chatbot

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
    question, chatbot, common_userinfo = await get_question_chatbot(event, bot, matcher)

    if chatbot.lock.locked():
        await send_message("这个bot已经有一个请求在执行中了,请等待结束后在询问它", matcher, bot, event)
        await matcher.finish()

    if len(question) < 7:
        question = question.replace(" ", "").replace("\n", "")
    if question in REFRESH_KEYWORDS:
        wait_msg = await reply_message(bot, matcher, event, "正在刷新，请稍等")
        async with chatbot.lock:
            try:
                await chatbot.refresh()
                msg = "刷新对话成功"
            except Exception as e:
                msg = str(e)
    else:
        if len(question) >= 1:
            async with chatbot.lock:
                wait_msg = await reply_message(bot, matcher, event, "正在思考，请稍等")

                try:
                    msg = await chatbot.ask(question=question)
                except Exception as e:
                    msg = str(e)
        else:
            msg = "你没有输入任何问题,请重新询问并在命令后加上问题"

    try:
        await delete_messages(bot, event, [wait_msg])
    except:
        # logger.error("撤回消息失败")
        pass
    reply = await reply_message(bot, matcher, event, msg, plain=False)
    temp_bots.set_bot_msgid(common_userinfo, chatbot, bot, event, reply)
    await matcher.finish()


new_bot = on_message(priority=1, block=False)


@new_bot.handle()
async def new_bot_(event: MessageEvent, matcher: Matcher, bot: Bot, state: T_State):
    from ...common.load_config import PRIVATE_COMMAND, PUBLIC_COMMAND, SPECIALPIC_WIDTH

    raw_message = str(event.message)
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
    state["able_source_dict"], able_source_str = get_able_source()
    state["replys"] = []
    path = await txt_to_pic(
        f"请输入要创建的bot的来源的序号\n可选项有:\n{able_source_str}输入'算了'或'取消'可以结束当前操作",
        width=SPECIALPIC_WIDTH + 400,
        quality=100,
    )
    state["replys"].append(await send_img(path, matcher, bot, event))


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
    from ...common.load_config import SPECIALPIC_WIDTH

    await if_close(event, matcher, bot, state["replys"])
    bot_nickname = str(args).replace("\n", "").replace("\r", "").replace(" ", "")
    if not is_valid_string(bot_nickname):
        await send_message("bot的名称不能包含特殊字符,只允许中文英文和数字,请重新开始", matcher, bot, event)
        await delete_messages(bot, event, state["replys"])
        await matcher.finish()
    else:
        state["bot_nickname"] = bot_nickname
    if not (
        state["able_source_dict"][state["source_index"]] == "bing"
        or state["able_source_dict"][state["source_index"]] == "bard"
        or state["able_source_dict"][state["source_index"]] == "通义千问"
    ):
        prompts_str = prompts.show_list()
        path = await txt_to_pic(
            f'请设置这个bot的预设\n如果不使用预设,请输入"无"或"无预设"\n如果使用本地预设,请在预设名前加".",如使用自己的预设直接发送即可\n当前可用的本地预设有\n{prompts_str}\n输入"算了"或"取消"可以结束当前操作',
            width=SPECIALPIC_WIDTH + 300,
            quality=100,
        )
        state["replys"].append(await send_img(path, matcher, bot, event))
    else:
        state["prompt_nickname"] = "无预设"
        matcher.set_arg("prompt", "")
        matcher.set_arg("prefix", "")


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
    except:
        pass
    if prompt in ["无", "无预设"]:
        prompt = ""
        prompt_nickname = "无预设"
    elif prompt.startswith("."):
        try:
            prompt_nickname = prompt.replace(".", "")
            prompt = prompts.show_prompt(prompt_nickname)
        except:
            await send_message("没有这个本地预设名", matcher, bot, event)
            await matcher.finish()

    state["replys"].append(
        await send_message(
            "请设置这个bot的前缀\n前缀是指每次对话时都在你的问题前添加一些要求内容,来使boy的回答符合要求\n注意前缀不可太长\n\n如果无需前缀,请输入\"无\"或\"无前缀\"\n如果需要前缀,请直接输入前缀内容\n输入'算了'或'取消'可以结束当前操作",
            matcher,
            bot,
            event,
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
    prefix = str(args)
    if prefix in ["无", "无前缀"]:
        prefix = ""

    common_userinfo = state["common_userinfo"]
    bot_nickname = state["bot_nickname"]

    prompt_nickname = state["prompt_nickname"]
    prompt = state["prompt"]

    botinfo = BotInfo(nickname=bot_nickname, onwer=common_userinfo)
    try:
        temp_bots.add_new_bot(
            common_userinfo=common_userinfo,
            botinfo=botinfo,
            botdata=BotData(
                nickname=bot_nickname,
                prompt_nickname=prompt_nickname,
                prompt=prompt,
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

    if not str(event.message).startswith(
        (f"{PRIVATE_COMMAND}删除bot", f"{PUBLIC_COMMAND}删除bot")
    ):
        await matcher.finish()
    if str(event.message).startswith(PRIVATE_COMMAND):
        state["common_userinfo"] = set_common_userinfo(event, bot)
        plain_message = (
            str(event.message).replace(f"{PRIVATE_COMMAND}删除bot", "").replace(" ", "")
        )
    else:
        await if_super_user(event, bot, matcher)
        state["common_userinfo"] = set_public_common_userinfo(bot)
        plain_message = (
            str(event.message).replace(f"{PUBLIC_COMMAND}删除bot", "").replace(" ", "")
        )
    state["replys"] = []
    if not plain_message:
        state["replys"].append(
            await send_message(
                "请输入bot的昵称,区分大小写\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event
            )
        )

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
    await if_close(event, matcher, bot, ["replys"])
    bot_name = str(args).replace("\n", "")
    common_userinfo = state["common_userinfo"]
    try:
        common_users.delete_bot(
            common_userinfo=common_userinfo,
            botinfo=BotInfo(nickname=bot_name, onwer=common_userinfo),
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

    if not str(event.message).startswith(
        (f"{PUBLIC_COMMAND}改名bot", f"{PRIVATE_COMMAND}改名bot")
    ):
        await matcher.finish()

    if str(event.message).startswith(PRIVATE_COMMAND):
        state["common_userinfo"] = set_common_userinfo(event=event, bot=bot)
    else:
        await if_super_user(event, bot, matcher)
        state["common_userinfo"] = set_public_common_userinfo(bot)
    state["replys"] = []
    state["replys"].append(
        await send_message("请输入要更改的bot的名称\n输入'取消'或'算了'可以结束当前操作", matcher, bot, event)
    )


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
        await send_message("bot名称不能包含特殊字符,请重新开始")
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
