import asyncio
from pathlib import Path
from nonebot.plugin import on_command, on_message
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import (
    Message,
    Event,
    Bot,
    MessageEvent,
    MessageSegment,
)
from .config import (
    BotInfo,
    PoeTemper,
    poe_persistor,
    get_user_info_and_data,
    set_userdata,
)
from .poe_func import (
    generate_truename,
    is_useable,
    send_msg,
    close_page,
    is_vip,
)
from .poe_api import poe_chat, poe_create, poe_clear
from ..common.common_func import delete_messages, is_nickname, is_public_nickname, reply_out, set_public_info_data
from ..common.config import spark_persistor
from ..common.render.render import md_to_pic
from ..chatgpt_web.config import gptweb_persistor
from .pwframework import pwfw
from nonebot import logger
sourcepath = Path(__file__).parent.parent / "source"

# 初始化两个需要使用的实例
temp_data = PoeTemper()
user_data_dict = temp_data.user_data_dict
msg_bot_bidict = temp_data.msg_bot_bidict
base_botinfo_dict = temp_data.base_botinfo_dict
prompts_dict = spark_persistor.prompts_dict
logger.info("开始加载poe")
templocks = {}
base_templocks = {}
tempuser_num = {}
######################################################
poe_auto_change_prompt = on_command(
    "poechangeprompt", aliases={"pcp"}, priority=4, block=False
)


@poe_auto_change_prompt.handle()
async def __poe_auto_change_prompt__(event: Event):
    global poe_persistor
    user_id = str(event.user_id)
    if user_id not in poe_persistor.superusers:
        await poe_auto_change_prompt.finish("你不是管理员哦")
    now_prompt = poe_persistor.auto_prompt
    str_prompts = str()
    i = 1
    for key, value in prompts_dict.items():
        str_prompts += f"*******************\n{i}:预设名称：{key}\n预设内容：{value}\n"
        i += 1
    await poe_auto_change_prompt.send(
        f"现在的自动创建预设是{now_prompt}\n当前可用预设有：\n{str_prompts}"
    )


@poe_auto_change_prompt.got("name", prompt="请输入要切换到的预设名称\n输入取消 或 算了可以终止创建")
async def __poe_auto_change_prompt____(
    matcher: Matcher, event: Event, state: T_State, infos: str = ArgStr("name")
):
    if not is_useable(event):
        await matcher.finish()
    if infos in ["取消", "算了"]:
        await poe_auto_change_prompt.finish("终止切换")
    infos = infos.split(" ")
    if len(infos) != 1 or infos[0] not in prompts_dict:
        await poe_auto_change_prompt.reject("你输入的信息有误，请检查后重新输入\n输入取消 或 算了可以终止切换,终止后不会再发送此消息")
    # 将更新后的字典写回到JSON文件中
    poe_persistor.auto_prompt = infos[0]
    poe_persistor.save()
    await poe_auto_change_prompt.finish("成功切换默认自动创建prompt")


######################################################
creat_lock = asyncio.Lock()
poe_create_ = on_command("poecreate", aliases={"pc"}, priority=4, block=False)


@poe_create_.handle()
async def __(matcher: Matcher, state: T_State, event: Event,args: Message = CommandArg()):
    global poe_persistor
    if not is_useable(event):
        await matcher.finish()
        
    is_public = False
    if str(args) == "public":
        if str(event.user_id) not in spark_persistor.superusers:
            await matcher.finish("你不是管理员，没有权限")
        is_public = True
    elif str(args):
        await matcher.finish("无意义后缀，请仅发送/加命令")
    state["public"] = is_public
    
    create_msgs = []
    if len(spark_persistor.prompts_dict) > 0:
        str_prompts = str()
        for key, _ in spark_persistor.prompts_dict.items():
            str_prompts += f"{key}\n"
        # create_msgs.append(await matcher.send(reply_out(event, f"当前预设有：\n{str_prompts}")))
        msg = f'当前预设有：\n{str_prompts}\n请输入\n1.机器人名称,\n2.基础模型选项，可选项为（gpt3_5输入1,claude输入2）,\n3.自定义预设（预设内容中间不要有空格） 或 "." + 可用本地预设名\n三个参数中间用空格隔开\n最终格式示例:\n示例一：chat 2 一个智能助理\n示例二： chat 1 .默认\n输入取消 或 算了可以终止创建'
    else:
        msg = f'当前没有可用本地预设\n\n请输入\n1.机器人名称,\n2.基础模型选项，可选项为（gpt3_5输入1,claude输入2）,\n3.自定义预设（预设内容中间不要有空格） 或 "." + 可用本地预设名\n三个参数中间用空格隔开\n最终格式示例:\n示例一：chat 2 一个智能助理\n示例二： chat 1 .默认\n输入取消 或 算了可以终止创建'
    create_msgs.append(await matcher.send(reply_out(event, msg)))
    state["create_msgs"] = create_msgs


@poe_create_.got("model")
async def __poe_create___(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    infos: str = ArgStr("model"),
):
    global poe_persistor
    create_msgs = state["create_msgs"]
    user_id = str(event.user_id)
    if infos in ["取消", "算了"]:
        create_msgs.append(await matcher.send(reply_out(event, "取消创建")))
        await delete_messages(bot, create_msgs)
        await poe_create_.finish()

    infos = infos.split(" ", 2)
    if not (len(infos) == 3 and infos[1] in ["1", "2"]):
        create_msgs.append(await matcher.send(reply_out(event, "输入信息有误，请检查后重新输入\n输入取消 或 算了可以终止创建,终止后不会再发送此消息")))
        await poe_create_.reject()

    # 获取创建所需信息

    nickname = str(infos[0])

    truename = str(generate_truename(user_id, nickname))
    prompt = str(infos[2])
    bot_index = str(infos[1])
    if bot_index == "1":
        model = "gpt3.5"
    else:
        model = "claude-instant"
    prompt_name = str("unknown")
    if prompt.startswith("."):
        prompt_name = prompt[1:]
        if prompt_name in spark_persistor.prompts_dict:
            prompt = spark_persistor.prompts_dict[prompt_name]
        else:
            create_msgs.append(
                await matcher.send(reply_out(event, "输入的本地预设名不正确，请重新输入\n输入取消 或 算了可以终止创建,终止后不会再发送此消息"))
            )
            await poe_create_.reject()
            
    if state["public"]:
        current_userinfo, current_userdata = set_public_info_data(user_data_dict)
    else:
        current_userinfo, current_userdata = set_userdata(event, user_data_dict)
        
    if current_userinfo not in list(poe_persistor.user_dict.keys()):
        poe_persistor.user_dict.setdefault(current_userinfo, {"all": {}, "now": {}})

    # 查看对应用户下是不是有重名的bot
    if state["public"]:
        if is_public_nickname(nickname
        ):
            create_msgs.append(
                await matcher.send(reply_out(event, "已经有同名的bot了，换一个名字重新输入吧\n输入取消 或 算了可以终止创建,终止后不会再发送此消息"))
            )
            await matcher.reject()
    else:
        if is_nickname(nickname,event
        ):
            create_msgs.append(
                await matcher.send(reply_out(event, "已经有同名的bot了，换一个名字重新输入吧\n输入取消 或 算了可以终止创建,终止后不会再发送此消息"))
            )
            await matcher.reject()
    if creat_lock.locked():
        waitmsg = await matcher.send(reply_out(event, "有人正在创建中，稍后自动为你创建"))
    async with creat_lock:
        page = await pwfw.new_page()
        is_created = await poe_create(
            page=page, botname=truename, base_bot_index=int(bot_index), prompt=prompt
        )
        await page.close()
        # is_created = True
        if is_created:
            # # 将更新后的字典写回到JSON文件中
            botinfo = BotInfo(
                nickname=nickname,
                truename=truename,
                source="poe",
                model=model,
                prompt_nickname=prompt_name,
                prompt=prompt,
                owner=str(event.user_id),
            )
            
            if state["public"]:
                botinfo.share = True
                botinfo.owner = "public"
                
            poe_persistor.user_dict.setdefault(current_userinfo, {}).setdefault(
                "all", {}
            )[nickname] = botinfo

            poe_persistor.user_dict[current_userinfo]["now"] = {nickname: botinfo}

            poe_persistor.save()
            try:
                await bot.delete_msg(message_id=waitmsg["message_id"])
            except:
                pass
            await matcher.send(reply_out(event, "创建成功并切换到新建bot"))

            await delete_messages(bot, create_msgs)
            await matcher.finish()
        else:
            await matcher.send(reply_out(event, "出错了，多次出错请联系机器人管理员"))

            await delete_messages(bot, create_msgs)
            await matcher.finish()


# ######################################################
poe_remove = on_command("poeremove", aliases={"pr"}, priority=4, block=False)


@poe_remove.handle()
async def __poe_remove__(
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
    if userinfo not in list(poe_persistor.user_dict.keys()):
        await matcher.finish(reply_out(event, "你还没创建任何bot"))

    # 如果有直接的arg的nickname，直接删除它，否则跳过
    if str(args):
        nickname = str(args[0])
        if nickname not in poe_persistor.user_dict[userinfo]["all"]:
            await matcher.finish(reply_out(event, "没有这个机器人呢"))
        if nickname == str(list(poe_persistor.user_dict[userinfo]["now"].keys())[0]):
            await matcher.finish(reply_out(event, "不能删除正在使用的bot哦"))
        del poe_persistor.user_dict[userinfo]["all"][nickname]
        msg = f"已删除{nickname}"
        await matcher.finish(reply_out(event, msg))

    bots = list(poe_persistor.user_dict[userinfo]["all"].keys())
    if len(bots) == 1:
        await matcher.finish(reply_out(event, f"当前只有一个机器人:{bots[0]},不能删除"))
    bot_nickname_str = "\n".join(str(bot) for bot in bots)

    nickname = str(list(poe_persistor.user_dict[userinfo]["now"].keys())[0])
    msg = (
        "你已经创建的的bot有：\n"
        + bot_nickname_str
        + f"\n当前使用的bot是{nickname}\n\n请输入要删除的机器人名称\n输入取消 或 算了可以终止创建"
    )
    remove_msgs.append(await matcher.send(reply_out(event, msg)))
    state["remove_msgs"] = remove_msgs
    state["userinfo"] = userinfo


@poe_remove.got("nickname")
async def __poe_remove____(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    infos: str = ArgStr("nickname"),
):
    userinfo = state["userinfo"]
    remove_msgs = state["remove_msgs"]
    bots = list(poe_persistor.user_dict[userinfo]["all"].keys())
    if infos in ["取消", "算了"]:
        remove_msgs.append(await matcher.send(reply_out(event, "终止删除")))

        await delete_messages(bot, remove_msgs)
        await matcher.finish()
    infos = infos.split(" ")
    nickname_delete = infos[0]
    nickname_now = str(list(poe_persistor.user_dict[userinfo]["now"].keys())[0])
    if not (nickname_delete in bots):
        remove_msgs.append(await matcher.send(reply_out(event, "输入信息有误，请检查后重新输入\n输入取消 或 算了可以终止删除,终止后不会再发送此消息")))
        await poe_remove.reject()
    if nickname_delete == nickname_now:
        remove_msgs.append(await matcher.send(reply_out(event, "不能删除正在使用的bot哦")))

        await delete_messages(bot, remove_msgs)
        await poe_remove.finish()
    del poe_persistor.user_dict[userinfo]["all"][nickname_delete]
    poe_persistor.save()

    await matcher.send(reply_out(event, f"已删除{nickname_delete}"))
    await delete_messages(bot, remove_msgs)
    await matcher.finish()


#############################################################
poe_switch = on_command("poeswitch", aliases={"ps"}, priority=4, block=False)


@poe_switch.handle()
async def __poe_switch__(
    bot: Bot,
    matcher: Matcher,
    event: Event,
    state: T_State,
    args: Message = CommandArg(),
):
    if not is_useable(event):
        await matcher.finish()
    if str(event.message).startswith(
        ("/psg", "/psn", "/psd", "/pss", "/psc+", "/psg4", "/psc")
    ):
        await matcher.finish()
    userinfo, _ = get_user_info_and_data(event)

    switch_msgs = []
    if userinfo not in list(poe_persistor.user_dict.keys()):
        await matcher.finish(reply_out(event, "你还没创建任何bot"))
    if args:
        nickname = str(args[0])
        if nickname not in poe_persistor.user_dict[userinfo]["all"].keys():
            switch_msgs.append(await matcher.finish(reply_out(event, "没有这个机器人呢")))

        poe_persistor.user_dict[userinfo]["now"] = {
            nickname: poe_persistor.user_dict[userinfo]["all"][nickname]
        }
        poe_persistor.save()
        await matcher.send(reply_out(event, f"已切换为{nickname}"))
        await delete_messages(bot, switch_msgs)
        await poe_switch.finish()

    bots = list(poe_persistor.user_dict[userinfo]["all"].keys())
    bot_str = "\n".join(str(bot) for bot in bots)

    nickname = str(list(poe_persistor.user_dict[userinfo]["now"].keys())[0])
    if len(bots) == 1:
        await matcher.finish(reply_out(event, f"当前只有一个bot:{nickname},无法切换"))
    msg = (
        "你已经创建的的bot有：\n"
        + bot_str
        + f"\n当前使用的bot是{nickname}\n\n请输入要切换的机器人名称\n输入取消 或 算了可以终止创建"
    )
    switch_msgs.append(await matcher.send(reply_out(event, msg)))

    state["switch_msgs"] = switch_msgs
    state["userinfo"] = userinfo


@poe_switch.got("nickname")
async def __poe_switch____(
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
        await delete_messages(bot, switch_msgs)
        await matcher.finish()

    nickname = infos.split(" ")[0]
    if nickname not in list(poe_persistor.user_dict[userinfo]["all"].keys()):
        switch_msgs.append(await matcher.send(reply_out(event, "没有这个机器人，请重新输入\n输入取消 或 算了可以终止切换,终止后不会再发送此消息")))
        await poe_switch.reject()

    poe_persistor.user_dict[userinfo]["now"] = {
        nickname: poe_persistor.user_dict[userinfo]["all"][nickname]
    }
    poe_persistor.save()
    await matcher.send(reply_out(event, f"已切换为{nickname}"))
    await delete_messages(bot, switch_msgs)
    await poe_switch.finish()


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
                if not is_useable(event):
                    return False
                if botinfo in list(base_botinfo_dict.values()):
                    mode = "public"
                elif botinfo.owner == "public":
                    mode = "private"
                elif botinfo.nickname in current_userdata.last_reply_message_id:
                    mode = "private"
                else:
                    return False
                try:
                    last_suggests = msg_bot_bidict[event.reply.message_id].last_suggests
                except:
                    last_suggests = []
                    #  mode,raw_message,last_msgid,last_suggests,nickname,truename,current_userinfo,current_userdata = temp
                return (
                    mode,
                    raw_message,
                    event.reply.message_id,
                    last_suggests,
                    botinfo.nickname,
                    botinfo.truename,
                    current_userinfo,
                    current_userdata,
                )
            except:
                return False
        else:
            return False
    elif str(event.message).startswith(("/pt", "/ptalk")):
        if not is_useable(event):
            return False
        raw_message = (
            str(event.message)
            .replace("/pchat ", "")
            .replace("/pchat", "")
            .replace("/pt ", "")
            .replace("/pt", "")
        )
        if not raw_message:
            return False
        mode = "private"
        try:
            botinfo = list(poe_persistor.user_dict[current_userinfo]["now"].values())[0]
            nickname = botinfo.nickname
            truename = botinfo.truename
        except:
            return "none"
        try:
            last_msgid = current_userdata.last_reply_message_id[nickname]
            last_suggests = msg_bot_bidict[last_msgid].last_suggests
        except:
            last_msgid = 0
            last_suggests = []
        return (
            mode,
            raw_message,
            last_msgid,
            last_suggests,
            nickname,
            truename,
            current_userinfo,
            current_userdata,
        )
    else:
        try:
            bots_nicknames = list(
                poe_persistor.user_dict[current_userinfo]["all"].keys()
            )
            nickname = next(
                (
                    name
                    for name in bots_nicknames
                    if str(event.message).startswith("/" + name)
                ),
                None,
            )
            mode = "private"
            if nickname:
                if not is_useable(event):
                    return False
                truename = poe_persistor.user_dict[current_userinfo]["all"][
                    nickname
                ].truename
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
                try:
                    last_suggests = msg_bot_bidict[last_msgid].last_suggests
                except:
                    last_suggests = []
                return (
                    mode,
                    raw_message,
                    last_msgid,
                    last_suggests,
                    nickname,
                    truename,
                    current_userinfo,
                    current_userdata,
                )
            else:
                pass
        except:
            pass
        try:
            bots_nicknames = list(base_botinfo_dict.keys())
            nickname = next(
                (
                    name
                    for name in base_botinfo_dict
                    if str(event.message).startswith("/" + name)
                ),
                None,
            )
            if nickname:
                if not is_useable(event):
                    return False
                truename = base_botinfo_dict[nickname].truename
                raw_message = (
                    str(event.message)
                    .replace("/" + nickname + " ", "")
                    .replace("/" + nickname, "")
                )
                if nickname in ["psg4", "psc+"] and not is_vip(event):
                    return False
                if not raw_message:
                    return False
                mode = "public"
                try:
                    last_msgid = current_userdata.last_reply_message_id[nickname]
                except:
                    last_msgid = 0
                try:
                    last_suggests = msg_bot_bidict[last_msgid].last_suggests
                except:
                    last_suggests = []
                return (
                    mode,
                    raw_message,
                    last_msgid,
                    last_suggests,
                    nickname,
                    truename,
                    current_userinfo,
                    current_userdata,
                )
            else:
                pass
        except:
            pass
        try:
            public_userinfo,public_userdata = set_public_info_data(user_data_dict)
            bots_nicknames = list(
                poe_persistor.user_dict[public_userinfo]["all"].keys()
            )
            nickname = next(
                (
                    name
                    for name in bots_nicknames
                    if str(event.message).startswith("/共享" + name) or str(event.message).startswith("/share" + name)
                ),
                None,
            )
            mode = "private"
            if nickname:
                if not is_useable(event):
                    return False
                truename = poe_persistor.user_dict[public_userinfo]["all"][
                    nickname
                ].truename
                raw_message = (
                    str(event.message)
                    .replace("/共享" + nickname + " ", "")
                    .replace("/共享" + nickname, "")
                    .replace("/share" + nickname + " ", "")
                    .replace("/share" + nickname, "")
                )
                if not raw_message:
                    return False
                try:
                    last_msgid = current_userdata.last_reply_message_id[nickname]
                except:
                    last_msgid = 0
                try:
                    last_suggests = msg_bot_bidict[last_msgid].last_suggests
                except:
                    last_suggests = []
                return (
                    mode,
                    raw_message,
                    last_msgid,
                    last_suggests,
                    nickname,
                    truename,
                    public_userinfo,
                    public_userdata,
                )
            else:
                return False
        except:
            return False


#############################################################
chat_lock = asyncio.Semaphore(3)
poe_base_lock = asyncio.Lock()
poe_chat_ = on_message(priority=1, block=False)


@poe_chat_.handle()
async def __chat_bot__(matcher: Matcher, event: MessageEvent, bot: Bot):
    temp = await _is_chat_(event, bot)
    if temp == False:
        await matcher.finish()
    if temp == "none":
        current_userinfo, current_userdata = set_userdata(
            event=event, user_data_dict=user_data_dict
        )
        if current_userdata.is_waiting:
            await matcher.finish(reply_out(event, "你已经有一个请求进行中了，请等结束后再发送"))
        mode = "private"
        user_id = str(event.user_id)
        raw_message = (
            str(event.message)
            .replace("/pchat ", "")
            .replace("/pchat", "")
            .replace("/pt ", "")
            .replace("/pt", "")
        )
        last_suggests = []
        nickname = "pdefault"
        truename = str(generate_truename(user_id, nickname))
        prompt_nickname = poe_persistor.auto_prompt
        prompt = spark_persistor.prompts_dict[prompt_nickname]
        current_userdata.is_waiting = True
        page = await pwfw.new_page()
        is_created = await poe_create(page, truename, 1, prompt)
        await page.close()
        current_userdata.is_waiting = False
        if is_created:
            # # 将更新后的字典写回到JSON文件中
            botinfo = BotInfo(
                nickname=nickname,
                truename=truename,
                source="poe",
                model="gpt3.5",
                prompt_nickname=prompt_nickname,
                prompt=prompt,
                owner="qq" + user_id,
            )
            poe_persistor.user_dict.setdefault(current_userinfo, {}).setdefault(
                "all", {}
            )["pdefault"] = botinfo
            poe_persistor.user_dict[current_userinfo]["now"] = {nickname: botinfo}

            poe_persistor.save()
            await matcher.send(reply_out(event, "自动创建gpt3.5机器人:pdefault成功"))
        else:
            await matcher.finish(reply_out(event, "自动创建出错，多次出错请联系机器人管理员"))
    else:
        (
            mode,
            raw_message,
            last_msgid,
            last_suggests,
            nickname,
            truename,
            current_userinfo,
            current_userdata,
        ) = temp
        try:
            botinfo = msg_bot_bidict[last_msgid]
        except:
            if mode == "private":
                botinfo = poe_persistor.user_dict[current_userinfo]["all"][nickname]
            else:
                botinfo = base_botinfo_dict[nickname]
    if len(raw_message) == 1 and raw_message in ["1", "2", "3", "4"] and last_suggests:
        text = last_suggests[int(raw_message) - 1]
    else:
        text = raw_message

    if mode == "private":
        if botinfo.owner != "public":
            if current_userdata.is_waiting:
                await matcher.finish(reply_out(event, "你已经有一个对话进行中了，请等结束后再发送"))
            if chat_lock.locked():
                await matcher.send(reply_out(event, "请稍等,你前面已有3个用户,你的回答稍后就来"))

            async with chat_lock:
                if text in ["清除对话", "清空对话", "清除历史", "清空历史", "清空历史对话", "刷新对话"]:
                    current_userdata.is_waiting = True
                    page = await pwfw.new_page()
                    is_cleared = await poe_clear(page=page, truename=truename)
                    await page.close()
                    current_userdata.is_waiting = False
                    if is_cleared:
                        msg = f"成功清除了{nickname}的历史消息"
                    else:
                        msg = "出错了，多次错误请联系机器人主人"
                    reply_msgid = await matcher.send(reply_out(event, msg))
                    current_userdata.last_reply_message_id[nickname] = reply_msgid[
                        "message_id"
                    ]
                    msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                    await matcher.finish()
                try:
                    wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
                except ActionFailed:
                    current_userdata.is_waiting = False
                    await matcher.finish()
                page = await pwfw.new_page()
                current_userdata.is_waiting = True
                result = await poe_chat(truename, text, page)
                await page.close()
                current_userdata.is_waiting = False
                
                await bot.delete_msg(message_id=wait_msg["message_id"])
                reply_msgid, chat_suggest_temp = await send_msg(result, matcher, event)
                current_userdata.last_reply_message_id[nickname] = reply_msgid["message_id"]
                if len(chat_suggest_temp) - 0:
                    botinfo.last_suggests = chat_suggest_temp
                msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                
                await matcher.finish()
        else:
            if botinfo.nickname not in list(templocks.keys()):
                templocks[botinfo.nickname] = asyncio.Lock()
            if botinfo.nickname not in list(tempuser_num.keys()):
                tempuser_num[botinfo.nickname] = 0
            lock = templocks[botinfo.nickname]
            if lock.locked() and tempuser_num[botinfo.nickname] <4:
                tempuser_num[botinfo.nickname] += 1
                wait_msg = await matcher.send(reply_out(event, "稍等，我还有一个问题没回发完，马上回复你"))
            elif lock.locked() and tempuser_num[botinfo.nickname] >= 4:
                wait_msg = await matcher.finish(reply_out(event, "我还有5个问题没回答呢，你等会再问吧"))
            else:
                tempuser_num[botinfo.nickname] += 1
            async with lock:
                if text in ["清除对话", "清空对话", "清除历史", "清空历史", "清空历史对话", "刷新对话"]:
                    page = await pwfw.new_page()
                    is_cleared = await poe_clear(page=page, truename=truename)
                    await page.close()
                    if is_cleared:
                        msg = f"成功清除了{nickname}的历史消息"
                    else:
                        msg = "出错了，多次错误请联系机器人主人"
                    tempuser_num[botinfo.nickname] -= 1
                    reply_msgid = await matcher.send(reply_out(event, msg))
                    current_userdata.last_reply_message_id[nickname] = reply_msgid[
                        "message_id"
                    ]
                    msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                    await matcher.finish()
                page = await pwfw.new_page()
                if tempuser_num[botinfo.nickname] == 1:
                    try:
                        wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
                    except ActionFailed:
                        current_userdata.is_waiting = False
                        await matcher.finish()
                result = await poe_chat(truename, text, page)
                await page.close()
                tempuser_num[botinfo.nickname] -= 1
                
                await bot.delete_msg(message_id=wait_msg["message_id"])
                reply_msgid, chat_suggest_temp = await send_msg(result, matcher, event)
                current_userdata.last_reply_message_id[nickname] = reply_msgid["message_id"]
                if len(chat_suggest_temp) - 0:
                    botinfo.last_suggests = chat_suggest_temp
                msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                
                await matcher.finish()
                

    elif mode == "public":
        if botinfo.nickname not in list(base_templocks.keys()):
            base_templocks[botinfo.nickname] = asyncio.Lock()
        lock = base_templocks[botinfo.nickname]
        if lock.locked() and base_botinfo_dict[nickname].num_users <4:
            base_botinfo_dict[nickname].num_users += 1
            wait_msg = await matcher.send(reply_out(event, "稍等，我还有一个问题没回发完，马上回复你"))
        elif lock.locked() and base_botinfo_dict[nickname].num_users >= 4:
            wait_msg = await matcher.finish(reply_out(event, "我还有5个问题没回答呢，你等会再问吧"))
        else:
            base_botinfo_dict[nickname].num_users += 1

        async with base_templocks[botinfo.nickname]:
            if text in ["清除对话", "清空对话", "清除历史", "清空历史", "清空历史对话", "刷新对话"]:
                current_userdata.is_waiting = True
                page = await pwfw.new_page()
                is_cleared = await poe_clear(page=page, truename=truename)
                await page.close()
                current_userdata.is_waiting = False
                base_botinfo_dict[nickname].num_users -= 1
                if is_cleared:
                    msg = f"成功清除了{truename}的历史消息"
                else:
                    msg = "出错了，多次错误请联系机器人主人"
                reply_msgid = await matcher.send(reply_out(event, msg))
                current_userdata.last_reply_message_id[nickname] = reply_msgid[
                    "message_id"
                ]
                msg_bot_bidict.inv[botinfo] = reply_msgid["message_id"]
                await matcher.finish()
            page = await pwfw.new_page()
            if base_botinfo_dict[nickname].num_users == 1:
                try:
                    wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
                except ActionFailed:
                    current_userdata.is_waiting = False
                    await matcher.finish() 
            result = await poe_chat(truename, text, page)
            await close_page(page)
            msgid, temp_suggests = await send_msg(result, matcher, event)
            base_botinfo_dict[nickname].num_users -= 1
            if len(temp_suggests) > 0:
                botinfo.last_suggests = temp_suggests

            msg_bot_bidict.inv[botinfo] = msgid["message_id"]
            try:
                await bot.delete_msg(message_id=wait_msg["message_id"])
            except:
                pass
            await matcher.finish()


######################################################
poe_help = on_command("poehelp", aliases={"p帮助", "ph"}, priority=4, block=False)


@poe_help.handle()
async def __poe_help__(bot: Bot, matcher: Matcher, event: Event):
    user_id = str(event.user_id)
    if not is_useable(event):
        await matcher.finish()
    msg = """
# spark-gpt Poe使用说明

- 共享的机器人供多人共同使用，而用户隔离的机器人每个人都是相互独立的。

- 以下命令前面全部要加 '/' ！！！！！

- 对话问答功能均支持以下特性：

- 可以通过回复机器人的最后一个回答来继续对话，而无需命令。
- 可以回复 "(清除/清空)(对话/历史)" 或"刷新对话"或"清除对话历史"来清空对话。
- 可以通过建议回复的数字索引来使用建议回复。

************************

- 以下命令均支持用户隔离

| 命令 | 描述 |
| --- | --- |
| `/ptalk / pt + 你要询问的内容` | 对话功能，如果没创建机器人，对话将自动创建默认机器人。 |
| `你的机器人的名字 + 空格 + 你要询问的内容` | 指定机器人对话。 |
| `/poecreate / pc` | 创建机器人。 |
| `/poeremove / pr (+ 机器人名称)` | 删除指定名称的机器人。 |
| `/poeswitch / ps (+ 机器人名称)` | 切换到指定名称的机器人。 |

************************

- 以下命令均是多用户共享的

| 命令 | 描述 |
| --- | --- |
| `/psg + 你要询问的内容` | 共享的GPT对话。 |
| `/psc + 你要询问的内容` | 共享的Claude-Instant对话。 |
| `/pss + 你要询问的内容` | 共享的Sage对话。 |
| `/psd + 你要询问的内容` | 共享的Dragonfly对话。 |
| `/psn + 你要搜索的内容` | (目前被删除，不可用)NeevaAI搜索引擎，返回链接及标题。 |

************************

- 以下功能仅限特定白名单用户使用，同样是多用户共享的

| 命令 | 描述 |
| --- | --- |
| `/psg4 + 询问内容` | 使用GPT4对话。 |
| `/pscp + 询问内容` | 使用CLAUDE+对话。 |
| `/psck + 询问内容` | 使用Claude-instant-100k对话。 |

************************

- 以下功能仅限poe管理员使用

| 命令 | 描述 |
| --- | --- |
| `/poechangeprompt / 切换自动预设 / pcp` | 切换自动创建的默认预设。 |
| `/poecreate / pc public` | 创建共享的机器人。 |

"""
    # pic = await md_to_pic(msg)
    # await matcher.send(MessageSegment.image(pic))
    await matcher.send(MessageSegment.image(Path(sourcepath / Path("demo(2).png")).absolute()))

    await poe_help.finish()
