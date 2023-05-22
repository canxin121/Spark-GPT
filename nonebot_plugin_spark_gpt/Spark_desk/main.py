import asyncio
from pathlib import Path
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


from .spark_desk_func import is_useable, sendmsg
from .config import (
    BotInfo,
    Spark_DeskTemper,
    spark_desk_persistor,
    get_user_info_and_data,
    set_userdata,
)
from .spark_api import sparkchat
from ..common.config import spark_persistor
from ..common.common_func import delete_messages, reply_out
from ..poe_pw.config import poe_persistor
from nonebot import logger
sourcepath = Path(__file__).parent.parent / "source"
# 初始化两个需要使用的实例
temp_data = Spark_DeskTemper()
user_data_dict = temp_data.user_data_dict
msg_bot_bidict = temp_data.msg_bot_bidict
prompts_dict = spark_persistor.prompts_dict
from ..common.render.render import md_to_pic

logger.info("开始加载spark_desk")


######################################################
creat_lock = asyncio.Lock()
spark_desk_create_ = on_command("screate", aliases={"sc"}, priority=4, block=False)


@spark_desk_create_.handle()
async def __(matcher: Matcher, state: T_State, event: Event):
    if not is_useable(event):
        await matcher.finish()
    create_msgs = []
    if len(prompts_dict) > 0:
        str_prompts = str()
        for key, _ in prompts_dict.items():
            str_prompts += f"{key}\n"
        # create_msgs.append(await matcher.send(reply_out(event, f"当前预设有：\n{str_prompts}")))
        msg = f'当前预设有：\n{str_prompts}\n请输入\n1.机器人名称,\n2.自定义预设（预设内容中间不要有空格） 或 "." + 可用本地预设名\n两个参数中间用空格隔开\n最终格式示例:\n示例1:猫娘 .猫娘\n示例2:chat 一个ai语言模型\n输入取消 或 算了可以终止创建'
    create_msgs.append(await matcher.send(reply_out(event, msg)))
    state["create_msgs"] = create_msgs


@spark_desk_create_.got("model")
async def __spark_desk_create___(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    infos: str = ArgStr("model"),
):
    global spark_desk_persistor
    create_msgs = state["create_msgs"]
    user_id = str(event.user_id)
    infos = infos.split(" ", 1)
    if infos[0] in ["取消", "算了"]:
        create_msgs.append(await matcher.send(reply_out(event, "取消创建")))
        await delete_messages(bot, str(event.user_id), create_msgs)
        await matcher.finish()
    if len(infos) != 2:
        create_msgs.append(await matcher.reject(reply_out(event, "你输入的信息有误，请重新输入\n输入取消 或 算了可以终止创建,终止后不会再发送此消息")))

    nickname = str(infos[0])
    truename = None
    prompt = str(infos[1])

    prompt_name = str("unknown")
    if prompt.startswith("."):
        prompt_name = prompt[1:]
        if prompt_name in prompts_dict:
            prompt = prompts_dict[prompt_name]
        else:
            create_msgs.append(
                await matcher.send(reply_out(event, "输入的本地预设名不正确，请重新输入\n输入取消 或 算了可以终止创建,终止后不会再发送此消息"))
            )
            await matcher.reject()

    current_userinfo, current_userdata = set_userdata(event, user_data_dict)
    if current_userinfo not in list(spark_desk_persistor.user_dict.keys()):
        spark_desk_persistor.user_dict.setdefault(
            current_userinfo, {"all": {}, "now": {}}
        )

    # 查看对应用户下是不是有重名的bot
    if (
        current_userinfo in spark_desk_persistor.user_dict
        and nickname in spark_desk_persistor.user_dict[current_userinfo]["all"]
    ) or (
        current_userinfo in poe_persistor.user_dict
        and nickname in poe_persistor.user_dict[current_userinfo]["all"]
    ):
        create_msgs.append(
            await matcher.send(reply_out(event, "已经有同名的bot了，换一个名字重新输入吧\n输入取消 或 算了可以终止创建,终止后不会再发送此消息"))
        )
        await matcher.reject()
    if creat_lock.locked():
        waitmsg = await matcher.send(reply_out(event, "有人正在创建中，稍后自动为你创建"))
    async with creat_lock:
        try:
            current_userdata.is_waiting = True
            chat_id = await sparkchat.generate_chat_id()
            result = await sparkchat.ask_question(chat_id, prompt)
            current_userdata.is_waiting = False
        except:
            current_userdata.is_waiting = False
            await matcher.send(reply_out(event, "出错了，多次出错请尝试换一个预设，还不行请联系机器人主人"))
            await delete_messages(bot, user_id, create_msgs)
        if result:
            # 将更新后的字典写回到JSON文件中
            botinfo = BotInfo(
                nickname=nickname,
                chat_id=chat_id,
                source="spark_desk",
                model="spark",
                prompt_nickname=prompt_name,
                prompt=prompt,
                owner="qq-" + str(event.user_id),
            )
            spark_desk_persistor.user_dict.setdefault(current_userinfo, {}).setdefault(
                "all", {}
            )[nickname] = botinfo

            spark_desk_persistor.user_dict[current_userinfo]["now"] = {
                nickname: botinfo
            }

            spark_desk_persistor.save()
            try:
                await bot.delete_msg(message_id=waitmsg["message_id"])
            except:
                pass
            reply_msgid = await matcher.send(
                reply_out(event, f"创建成功并切换到新建bot\n\n创建自动回复:{result}")
            )
            msg_bot_bidict[reply_msgid["message_id"]] = botinfo
            current_userdata.last_reply_message_id[nickname] = reply_msgid["message_id"]
            await delete_messages(bot, user_id, create_msgs)
            current_userdata.is_waiting = False
            await matcher.finish()
        else:
            await matcher.send(reply_out(event, "出错了，多次出错请联系机器人管理员"))

            await delete_messages(bot, user_id, create_msgs)
            current_userdata.is_waiting = False
            await matcher.finish()


#############################################################
spark_desk_switch = on_command("sswitch", aliases={"ss"}, priority=4, block=False)


@spark_desk_switch.handle()
async def __spark_desk_switch__(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    args: Message = CommandArg(),
):
    if not is_useable(event):
        await matcher.finish()
    userinfo, _ = get_user_info_and_data(event)
    switch_msgs = []
    if userinfo not in list(spark_desk_persistor.user_dict.keys()):
        await matcher.finish(reply_out(event, "你还没创建任何bot"))
    if args:
        nickname = str(args[0])
        if nickname not in spark_desk_persistor.user_dict[userinfo]["all"].keys():
            switch_msgs.append(await matcher.finish(reply_out(event, "没有这个机器人呢")))

        spark_desk_persistor.user_dict[userinfo]["now"] = {
            nickname: spark_desk_persistor.user_dict[userinfo]["all"][nickname]
        }
        spark_desk_persistor.save()
        await matcher.send(reply_out(event, f"已切换为{nickname}"))
        await delete_messages(bot, userinfo, switch_msgs)
        await spark_desk_switch.finish()

    spark_desk_bots = list(spark_desk_persistor.user_dict[userinfo]["all"].keys())
    spark_desk_bot_str = "\nspark_desk机器人有:\n" + "\n".join(
        str(bot) for bot in spark_desk_bots
    )
    nickname = str(list(spark_desk_persistor.user_dict[userinfo]["now"].keys())[0])
    if len(spark_desk_bots) == 1:
        await matcher.finish(reply_out(event, f"当前只有一个bot:{nickname},无法切换"))
    msg = (
        "你已经创建的的bot有：\n"
        + spark_desk_bot_str
        + f"\n当前使用的bot是{nickname}\n\n请输入要切换的机器人名称\n输入取消 或 算了可以终止创建"
    )
    switch_msgs.append(await matcher.send(reply_out(event, msg)))
    state["switch_msgs"] = switch_msgs
    state["userinfo"] = userinfo


@spark_desk_switch.got("nickname")
async def __spark_desk_switch____(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    infos: str = ArgStr("nickname"),
):
    switch_msgs = state["switch_msgs"]
    userinfo = state["userinfo"]

    if infos in ["取消", "算了"]:
        switch_msgs.append(await matcher.send(reply_out(event, "终止切换")))
        await delete_messages(bot, userinfo, switch_msgs)
        await matcher.finish()

    nickname = infos.split(" ")[0]
    if nickname not in list(spark_desk_persistor.user_dict[userinfo]["all"].keys()):
        switch_msgs.append(await matcher.send(reply_out(event, "没有这个机器人，请重新输入\n输入取消 或 算了可以终止切换,终止后不会再发送此消息")))
        await spark_desk_switch.reject()

    spark_desk_persistor.user_dict[userinfo]["now"] = {
        nickname: spark_desk_persistor.user_dict[userinfo]["all"][nickname]
    }
    spark_desk_persistor.save()
    await matcher.send(reply_out(event, f"已切换为{nickname}"))
    await delete_messages(bot, userinfo, switch_msgs)
    await spark_desk_switch.finish()


#############################################################
async def _is_chat_(event: MessageEvent, bot: Bot):
    # 处理用命令来进行的对话,包括pt，指定名，公共的，也可以处理回复形式的对话
    try:
        current_userinfo, current_userdata = set_userdata(
            event=event, user_data_dict=user_data_dict
        )
    except:
        return False
    if bool(event.reply):
        if str(event.reply.sender.user_id) == bot.self_id:
            raw_message = str(event.message)
            if not raw_message:
                return False
            try:
                botinfo = msg_bot_bidict[event.reply.message_id]
                if botinfo.nickname in current_userdata.last_reply_message_id:
                    if not is_useable(event):
                        return False
                    return (
                        event.reply.message_id,
                        raw_message,
                        botinfo,
                        current_userinfo,
                        current_userdata,
                    )
                else:
                    return False
            except:
                return False
        else:
            return False
    elif str(event.message).startswith(("/st", "/sparktalk")):
        if not is_useable(event):
            return False
        raw_message = (
            str(event.message)
            .replace("/sparkalk ", "")
            .replace("/sparkalk", "")
            .replace("/st ", "")
            .replace("/st", "")
        )
        if not raw_message:
            return False
        try:
            botinfo = list(
                spark_desk_persistor.user_dict[current_userinfo]["now"].values()
            )[0]
            nickname = botinfo.nickname
        except:
            return "none"
        try:
            last_msgid = current_userdata.last_reply_message_id[nickname]
        except:
            last_msgid = 0
        return last_msgid, raw_message, botinfo, current_userinfo, current_userdata
    else:
        try:
            bots_nicknames = list(
                spark_desk_persistor.user_dict[current_userinfo]["all"].keys()
            )
            nickname = next(
                (
                    name
                    for name in bots_nicknames
                    if str(event.message).startswith("/" + name)
                ),
                None,
            )
            if nickname:
                if not is_useable(event):
                    return False
                botinfo = spark_desk_persistor.user_dict[current_userinfo]["all"][
                    nickname
                ]
                raw_message = (
                    str(event.message)
                    .replace("/" + nickname + " ", "")
                    .replace("/" + nickname, "")
                )
                if not raw_message:
                    return False
                try:
                    last_msgid = current_userdata.last_reply_message_id[nickname]
                except:
                    last_msgid = 0
                return (
                    last_msgid,
                    raw_message,
                    botinfo,
                    current_userinfo,
                    current_userdata,
                )
            else:
                return False
        except:
            return False


#############################################################
chat_lock = asyncio.Semaphore(3)

spark_desk_chat_ = on_message(priority=1, block=False)


@spark_desk_chat_.handle()
async def __chat_bot__(matcher: Matcher, event: MessageEvent, bot: Bot):
    temp = await _is_chat_(event, bot)
    if temp == False:
        await matcher.finish()
    if temp == "none":
        current_userinfo, current_userdata = set_userdata(event, user_data_dict)
        if current_userdata.is_waiting:
            await matcher.finish(reply_out(event, "你已经有一个请求进行中了，请等结束后再发送"))
        nickname = "spark_deskdefault"
        prompt_nickname = spark_desk_persistor.auto_prompt
        prompt = prompts_dict[prompt_nickname]
        raw_message = (
            str(event.message)
            .replace("/sparkalk ", "")
            .replace("/sparkalk", "")
            .replace("/spark ", "")
            .replace("/spark", "")
        )
        lastmsg_id = 0
        if current_userinfo not in list(spark_desk_persistor.user_dict.keys()):
            spark_desk_persistor.user_dict.setdefault(
                current_userinfo, {"all": {}, "now": {}}
            )

        try:
            current_userdata.is_waiting = True
            chat_id = await sparkchat.generate_chat_id()
            wait_msg = await matcher.send(reply_out(event, "正在自动创建，请稍等"))
            result = await sparkchat.ask_question(chat_id, prompt)
            current_userdata.is_waiting = False
        except:
            current_userdata.is_waiting = False
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
        if result:
            # 将更新后的字典写回到JSON文件中
            botinfo = BotInfo(
                nickname=nickname,
                chat_id=chat_id,
                source="spark_desk",
                model="spark",
                prompt_nickname=prompt_nickname,
                prompt=prompt,
                owner="qq-" + str(event.user_id),
            )
            spark_desk_persistor.user_dict.setdefault(
                current_userinfo, {}
            ).setdefault("all", {})[nickname] = botinfo
            spark_desk_persistor.user_dict.setdefault(
                current_userinfo, {}
            ).setdefault("now", {})[nickname] = botinfo
            spark_desk_persistor.save()
            try:
                await bot.delete_msg(message_id=wait_msg["message_id"])
            except:
                pass
            await matcher.send(
                reply_out(
                    event, f"自动创建成功并切换到新建bot:spark_deskdefault\n自动创建回复:\n{result}"
                )
            )
            await bot.delete_msg(message_id = wait_msg["message_id"])
        else:
            current_userdata.is_waiting = False
            await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
    else:
        lastmsg_id, raw_message, botinfo, current_userinfo, current_userdata = temp
    nickname = botinfo.nickname
    chat_id = botinfo.chat_id
    if current_userdata.is_waiting:
        await matcher.finish(reply_out(event, "你已经有一个请求进行中了，请等结束后再发送"))
    if chat_lock.locked():
        await matcher.send(reply_out(event, "请稍等,你前面已有3个用户,你的回答稍后就来"))

    async with chat_lock:
        if raw_message in [
            "清除对话",
            "清空对话",
            "清除历史",
            "清空历史",
            "清除记录",
            "清空历史对话",
            "刷新对话",
        ]:
            prompt = botinfo.prompt
            if current_userinfo not in list(spark_desk_persistor.user_dict.keys()):
                spark_desk_persistor.user_dict.setdefault(
                    current_userinfo, {"all": {}, "now": {}}
                )

            try:
                current_userdata.is_waiting = True
                chat_id = await sparkchat.generate_chat_id()
                wait_msg = await matcher.send(reply_out(event, "正在刷新，请稍等"))
                result = await sparkchat.ask_question(chat_id, prompt)
                current_userdata.is_waiting = False
            except Exception as e:
                current_userdata.is_waiting = False
                await matcher.finish(reply_out(event, f"出错了:{e},多次尝试都出错请联系机器人管理员"))
            if result:
                botinfo.chat_id = chat_id
                spark_desk_persistor.user_dict[current_userinfo]["all"][
                    nickname
                ] = botinfo
                if (
                    botinfo.nickname
                    == list(
                        spark_desk_persistor.user_dict[current_userinfo][
                            "now"
                        ].values()
                    )[0].nickname
                ):
                    spark_desk_persistor.user_dict[current_userinfo]["now"] = {
                        nickname: botinfo
                    }
                spark_desk_persistor.save()
                msg_bot_bidict[lastmsg_id] = botinfo

                reply_msgid = await matcher.send(
                    reply_out(event, f"刷新对话成功\n刷新回复:\n{result}")
                )
                current_userdata.last_reply_message_id[nickname] = reply_msgid[
                    "message_id"
                ]
                await bot.delete_msg(message_id=wait_msg["message_id"])

                msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                await matcher.finish()
            else:
                await matcher.finish(reply_out(event, "出错了，多次出错请联系机器人管理员"))
        else:
            current_userdata.is_waiting = True
            try:
                chat_id = botinfo.chat_id
                wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
                result = await sparkchat.ask_question(chat_id, raw_message)
                await bot.delete_msg(message_id=wait_msg["message_id"])
                current_userdata.is_waiting = False
            except Exception as e:
                current_userdata.is_waiting = False
                await matcher.finish(reply_out(event, f"出错了{e}，多次出错请联系机器人主人"))
            if result:
                reply_msgid = await sendmsg(result, matcher, event)
                current_userdata.last_reply_message_id[nickname] = reply_msgid[
                    "message_id"
                ]
                msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                await matcher.finish()
            else:
                await matcher.finish(reply_out(event, f"出错了:没有返回值，刷新对话试试，多次出错请联系机器人主人"))


# ######################################################
spark_desk_remove = on_command("sparkremove", aliases={"sr"}, priority=4, block=False)


@spark_desk_remove.handle()
async def __spark_desk_remove__(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    args: Message = CommandArg(),
):
    if not is_useable(event):
        await matcher.finish()
    userinfo, _ = get_user_info_and_data(event)

    remove_msgs = []
    if userinfo not in list(spark_desk_persistor.user_dict.keys()):
        await matcher.finish(reply_out(event, "你还没创建任何bot"))

    # 如果有直接的arg的nickname，直接删除它，否则跳过
    if str(args):
        nickname = str(args[0])
        if nickname not in spark_desk_persistor.user_dict[userinfo]["all"]:
            await matcher.finish(reply_out(event, "没有这个机器人呢"))
        if nickname == str(
            list(spark_desk_persistor.user_dict[userinfo]["now"].keys())[0]
        ):
            await matcher.finish(reply_out(event, "不能删除正在使用的bot哦"))
        del spark_desk_persistor.user_dict[userinfo]["all"][nickname]
        msg = f"已删除{nickname}"
        await matcher.finish(reply_out(event, msg))

    bots = list(spark_desk_persistor.user_dict[userinfo]["all"].keys())
    if len(bots) == 1:
        await matcher.finish(reply_out(event, f"当前只有一个机器人:{bots[0]},不能删除"))
    bot_nickname_str = "\n".join(str(bot) for bot in bots)

    nickname = str(list(spark_desk_persistor.user_dict[userinfo]["now"].keys())[0])
    msg = (
        "你已经创建的的bot有：\n"
        + bot_nickname_str
        + f"\n当前使用的bot是{nickname}\n\n请输入要删除的机器人名称\n输入取消 或 算了可以终止创建"
    )
    remove_msgs.append(await matcher.send(reply_out(event, msg)))
    state["remove_msgs"] = remove_msgs
    state["userinfo"] = userinfo


@spark_desk_remove.got("nickname")
async def __spark_desk_remove____(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    infos: str = ArgStr("nickname"),
):
    if not is_useable(event):
        await matcher.finish()
    userinfo = state["userinfo"]
    remove_msgs = state["remove_msgs"]
    bots = list(spark_desk_persistor.user_dict[userinfo]["all"].keys())
    if infos in ["取消", "算了"]:
        remove_msgs.append(await matcher.send(reply_out(event, "终止删除")))

        await delete_messages(bot, str(event.user_id), remove_msgs)
        await matcher.finish()
    infos = infos.split(" ")
    nickname_delete = infos[0]
    nickname_now = str(list(spark_desk_persistor.user_dict[userinfo]["now"].keys())[0])
    if not (nickname_delete in bots):
        remove_msgs.append(await matcher.send(reply_out(event, "输入信息有误，请检查后重新输入\n输入取消 或 算了可以终止删除,终止后不会再发送此消息")))
        await spark_desk_remove.reject()
    if nickname_delete == nickname_now:
        remove_msgs.append(await matcher.send(reply_out(event, "不能删除正在使用的bot哦")))

        await delete_messages(bot, userinfo, remove_msgs)
        await spark_desk_remove.finish()
    del spark_desk_persistor.user_dict[userinfo]["all"][nickname_delete]
    spark_desk_persistor.save()

    await matcher.send(reply_out(event, f"已删除{nickname_delete}"))
    await delete_messages(bot, userinfo, remove_msgs)
    await matcher.finish()


######################################################
spark_desk_auto_change_prompt = on_command(
    "schangeprompt", aliases={"scp"}, priority=4, block=False
)


@spark_desk_auto_change_prompt.handle()
async def __poe_auto_change_prompt__(matcher: Matcher, event: Event):
    if not is_useable(event):
        await matcher.finish()
    global spark_desk_persistor
    user_id = str(event.user_id)
    if user_id not in spark_desk_persistor.superusers:
        await spark_desk_auto_change_prompt.finish("你不是管理员哦")
    now_prompt = spark_desk_persistor.auto_prompt
    str_prompts = str()
    i = 1
    for key, value in prompts_dict.items():
        str_prompts += f"*******************\n{i}:预设名称：{key}\n预设内容：{value}\n"
        i += 1
    await spark_desk_auto_change_prompt.send(
        f"现在的自动创建预设是:{now_prompt}\n当前可用预设有：\n{str_prompts}"
    )


@spark_desk_auto_change_prompt.got("name", prompt="请输入要切换到的预设名称\n输入取消 或 算了可以终止创建")
async def __poe_auto_change_prompt____(
    event: Event, state: T_State, infos: str = ArgStr("name")
):
    if infos in ["取消", "算了"]:
        await spark_desk_auto_change_prompt.finish("终止切换")
    infos = infos.split(" ")
    if len(infos) != 1 or infos[0] not in prompts_dict:
        await spark_desk_auto_change_prompt.reject("你输入的信息有误，请检查后重新输入\n输入取消 或 算了可以终止切换,终止后不会再发送此消息")
    # 将更新后的字典写回到JSON文件中
    spark_desk_persistor.auto_prompt = infos[0]
    spark_desk_persistor.save()
    await spark_desk_auto_change_prompt.finish("成功切换默认自动创建prompt")

######################################################
spark_desk_help = on_command(
    "sparkhelp", aliases={"s帮助", "sh"}, priority=4, block=False
)


@spark_desk_help.handle()
async def __spark_desk_help__(bot: Bot, matcher: Matcher, event: Event):
    if str(event.message).startswith("/share"):
        await matcher.finish()
        
    user_id = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    msg = """
# spark-gpt Spark_desk使用说明

- !!! 以下命令前面全部要加 '/' !!!  

- 问答功能均支持以下特性：
- 可以通过回复机器人的最后一个回答来继续对话，而无需命令；可以回复 "(清除/清空)(对话/历史)"或 "刷新对话" 或 "清除对话历史"来清空对话；  
- 可以通过建议回复的数字索引来使用建议回复。

## 对话命令

| 命令 | 描述 |
| --- | --- |
| `/sparktalk / st + 你要询问的内容` | 对话功能，如果没创建机器人，对话将自动创建默认机器人。 |
| `/机器人名字 + 空格 + 你要询问的内容` | 指定机器人对话。 |

## 机器人管理命令

| 命令 | 描述 |
| --- | --- |
| `/screate / sc` | 创建机器人。 |
| `/sparkremove / sr (+ 机器人名称)` | 删除指定名称的机器人。 |
| `/sparkswitch / ss (+ 机器人名称)` | 切换到指定名称的机器人。 |

## 管理员命令

- 仅限spark_desk管理员使用

| 命令 | 描述 |
| --- | --- |
| `/scp / schangeprompt` | 切换自动创建的默认预设。 |"""
    # pic = await md_to_pic(msg)
    await matcher.send(MessageSegment.image(Path(sourcepath / Path("demo(6).png")).absolute()))

    await spark_desk_help.finish()
