import json
from pathlib import Path
from typing import Literal
from nonebot.exception import ActionFailed, NetworkError
from nonebot import logger
from nonebot.plugin import on_command, on_message, on
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
from .utils import (
    if_super_user,
    set_common_userinfo,
    set_public_common_userinfo,
    set_userinfo,
    delete_messages,
    reply_out,
    if_close,
)
from ...common.user_data import common_users
from ...common.prompt_data import prompts
from .userlinks import users
from ...common.mytypes import UserInfo, CommonUserInfo, BotInfo, BotData
from ..temp_data import temp_bots
from ...api_utils.load_config import get_able_source

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
    raw_text = str(event.message)
    if not (raw_text.startswith(("/", ".")) or bool(event.reply)):
        await matcher.finish()
    if bool(event.reply):
        if str(event.reply.sender.user_id) == bot.self_id:
            question = raw_text
            try:
                common_userinfo = set_common_userinfo(event)
                chatbot = temp_bots.get_bot_by_msgid(
                    common_userinfo=common_userinfo, message_id=event.reply.message_id
                )
            except:
                await matcher.finish()
            try:
                common_userinfo = set_public_common_userinfo()
                chatbot = temp_bots.get_bot_by_msgid(
                    common_userinfo=common_userinfo, message_id=event.reply.message_id
                )
            except:
                await matcher.finish()
        else:
            await matcher.finish()
    else:
        if raw_text.startswith("/"):
            common_userinfo = set_common_userinfo(event)
        elif raw_text.startswith("."):
            common_userinfo = set_public_common_userinfo()
        try:
            question, chatbot = temp_bots.get_bot_by_text(
                common_userinfo=common_userinfo, text=raw_text
            )
        except Exception as e:
            # logger.error(str(e))
            await matcher.finish()

    if chatbot.is_waiting:
        await matcher.finish(reply_out(event, "这个bot已经有一个请求在执行中了,请等待结束后在询问它"))
    if len(question) < 7:
        question = question.replace(" ", "").replace("\n", "")
    if question in REFRESH_KEYWORDS:
        wait_msg = await matcher.send(reply_out(event, "正在刷新，请稍等"))
        try:
            await chatbot.refresh()
            msg = "刷新对话成功"
        except Exception as e:
            msg = str(e)
    else:
        try:
            wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
            msg = await chatbot.ask(question=question)
        except Exception as e:
            msg = str(e)
    try:
        await delete_messages(bot, [wait_msg])
    except:
        logger.error("撤回消息失败")
        pass
    reply = await matcher.send(reply_out(event, msg))
    temp_bots.set_bot_msgid(common_userinfo, chatbot, str(reply["message_id"]))
    await matcher.finish()


new_bot = on_message(priority=1, block=False)


@new_bot.handle()
async def new_bot_(event: Event, matcher: Matcher, state: T_State):
    raw_message = str(event.message)
    if not raw_message.startswith((".创建bot", "/创建bot")):
        await matcher.finish()
    if raw_message.startswith("."):
        state["pre_command"] = "."
        state["common_userinfo"] = set_public_common_userinfo()
    else:
        state["pre_command"] = "/"
        state["common_userinfo"] = set_common_userinfo(event)
    state["able_source_dict"], able_source_str = get_able_source()
    state["replys"] = []
    state["replys"].append(
        await matcher.send(
            MessageSegment.text(
                f"请输入要创建的bot的来源的序号\n可选项有:\n{able_source_str}输入'算了'或'取消'可以结束当前操作"
            )
        )
    )


@new_bot.got("source_index")
async def new_bot__(
    matcher: Matcher,
    event: Event,
    state: T_State,
    bot: Bot,
    args: str = ArgStr("source_index"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["source_index"] = str(args).replace("\n", "")
    if state["source_index"] not in [
        str(i) for i in range(1, len(state["able_source_dict"]) + 1)
    ]:
        await matcher.send("没有这个索引数字,请从头开始")
        await delete_messages(bot, state["replys"])
        await matcher.finish()
    state["replys"].append(
        await matcher.send(
            MessageSegment.text("请为这个新bot设置一个独一无二的昵称\n输入'算了'或'取消'可以结束当前操作")
        )
    )


@new_bot.got("bot_nickname")
async def new_bot___(
    matcher: Matcher,
    event: Event,
    state: T_State,
    bot: Bot,
    args: str = ArgStr("bot_nickname"),
):
    await if_close(event, matcher, bot, state["replys"])
    state["bot_nickname"] = str(args).replace("\n", "")
    if not (
        state["able_source_dict"][state["source_index"]] == "bing"
        or state["able_source_dict"][state["source_index"]] == "bard"
    ):
        prompts_str = prompts.show_list()
        state["replys"].append(
            await matcher.send(
                MessageSegment.text(
                    f'请设置这个bot的预设\n如果使用本地预设,请在预设名前加".",如使用自己的预设直接发送即可\n当前可用的本地预设有\n{prompts_str}\n输入"算了"或"取消"可以结束当前操作'
                )
            )
        )
    else:
        matcher.set_arg("prompt", "no prompt")


@new_bot.got("prompt")
async def new_bot____(
    matcher: Matcher,
    state: T_State,
    bot: Bot,
    event: Event,
    args: str = ArgStr("prompt"),
):
    await if_close(event, matcher, bot, state["replys"])
    prompt = str(args).replace("\n", "")
    if prompt.startswith("."):
        try:
            prompt = prompts.show_prompt(prompt_name=prompt.replace(".", ""))
        except:
            await matcher.finish("没有这个本地预设名")
    bot_nickname = state["bot_nickname"]
    common_userinfo = state["common_userinfo"]
    botinfo = BotInfo(nickname=bot_nickname, onwer=common_userinfo)
    try:
        temp_bots.add_new_bot(
            common_userinfo=common_userinfo,
            botinfo=botinfo,
            botdata=BotData(
                nickname=bot_nickname,
                prompt=prompt,
                source=state["able_source_dict"][state["source_index"]],
            ),
        )
        pre_command = state["pre_command"]
        msg = f"成功添加了bot,使用命令{pre_command}{bot_nickname}加上你要询问的内容即可使用该bot"
        await matcher.finish(MessageSegment.text(msg))
    except MatcherException:
        await delete_messages(bot, state["replys"])
        raise
    except Exception as e:
        await matcher.finish(str(e))


delete_bot = on_message(priority=1, block=False)


@delete_bot.handle()
async def delete_bot_(matcher: Matcher, event: MessageEvent, state: T_State):
    if not str(event.message).startswith(("/删除bot", ".删除bot")):
        await matcher.finish()
    if str(event.message).startswith("/"):
        state["common_userinfo"] = set_common_userinfo(event=event)
        plain_message = str(event.message).replace("/删除bot", "").replace(" ", "")
    else:
        await if_super_user(event, matcher)
        state["common_userinfo"] = set_public_common_userinfo()
        plain_message = str(event.message).replace(".删除bot", "").replace(" ", "")
    state["replys"] = []
    if not plain_message:
        state["replys"].append(
            await matcher.send(
                MessageSegment.text("请输入bot的昵称,区分大小写\n输入'取消'或'算了'可以结束当前操作")
            )
        )
    else:
        matcher.set_arg("bot", plain_message)


@delete_bot.got("bot")
async def delete_bot__(
    matcher: Matcher, state: T_State, bot: Bot, event: Event, args: str = ArgStr("bot")
):
    await if_close(event, matcher, bot, state["replys"])
    bot_name = str(args).replace("\n", "")
    common_userinfo = state["common_userinfo"]
    try:
        common_users.delete_bot(
            common_userinfo=common_userinfo,
            botinfo=BotInfo(nickname=bot_name, onwer=common_userinfo),
        )
        await matcher.finish(MessageSegment.text("成功删除了该bot"))
    except MatcherException:
        await delete_messages(bot, state["replys"])
        raise
    except Exception as e:
        await matcher.finish(str(e))
