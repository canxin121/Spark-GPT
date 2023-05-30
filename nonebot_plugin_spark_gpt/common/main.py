import asyncio
from pathlib import Path

from nonebot.plugin import on_command
from nonebot.params import ArgStr
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Event, Message, MessageSegment, Bot
from nonebot.params import ArgStr, CommandArg
from .render.render import md_to_pic
from .config import spark_persistor, get_user_info_and_data
from .common_func import (
    get_public_info_data,
    is_auto_prompt,
    get_botinfo,
    is_nickname,
    is_public_nickname,
    reply_out,
    delete_messages,
    set_public_info_data,
    get_public_botinfo,
)
from ..chatgpt_web.config import gptweb_persistor

from ..claude_slack.config import claude_slack_persistor
from ..Spark_desk.config import spark_desk_persistor

if spark_persistor.poe_api_mode == 0:
    from ..poe_http.main import run_poe_change
    from ..poe_http.config import poe_persistor
else:
    from ..poe_pw.config import poe_persistor
    from ..poe_pw.poe_api import poe_change
    from ..poe_pw.pwframework import pwfw
spark_addprompt = on_command("添加预设", aliases={"ap"}, priority=4, block=False)

sourcepath = str(Path(__file__).parent / "source")


@spark_addprompt.handle()
async def __spark_addprompt__(state:T_State,matcher: Matcher, event: Event):
    global spark_persistor
    replys = []
    user_id = str(event.user_id)
    if user_id not in spark_persistor.superusers:
        await spark_addprompt.finish("你不是管理员哦")
    replys.append(await matcher.send("请输入预设名称\n输入取消 或 算了可以终止添加"))
    state["replys"] = replys

@spark_addprompt.got("name")
async def __spark_addprompt____(
    matcher:Matcher,event: Event,bot:Bot, state: T_State, infos: str = ArgStr("name")
):
    replys = state["replys"]
    global spark_persistor
    if infos in ["取消", "算了"]:
        await delete_messages(bot,replys)
        await spark_addprompt.finish("终止添加")
    infos = infos.split(" ")
    if len(infos) != 1:
        replys.append(await spark_addprompt.send("你输入的信息有误，请检查后重新输入\n输入取消 或 算了可以终止添加,终止后不会再发送此消息"))
        await matcher.reject()
    replys.append(await matcher.send("请输入预设\n输入取消 或 算了可以终止创建"))
    state["key"] = infos[0]
    state["replys"] = replys


@spark_addprompt.got(
    "prompt"
)
async def __spark_addprompt____(
    event: Event, bot:Bot,state: T_State, infos: str = ArgStr("prompt")
):
    global spark_persistor
    replys = state["replys"]
    if infos in ["取消", "算了"]:
        await delete_messages(bot,replys)
        await spark_addprompt.finish("终止添加")
    name = state["key"]
    prompt = infos
    # # 将更新后的字典写回到JSON文件中
    spark_persistor.prompts_dict[name] = prompt
    spark_persistor.save()
    await delete_messages(bot,replys)
    await spark_addprompt.finish("成功添加prompt")


spark_removeprompt = on_command("删除预设", aliases={"rp"}, priority=4, block=False)


@spark_removeprompt.handle()
async def __spark_removeprompt__(
    event: Event, state: T_State, args: Message = CommandArg()
):
    global spark_persistor
    user_id = str(event.user_id)
    if user_id not in spark_persistor.superusers:
        await spark_removeprompt.finish("你不是管理员哦")
    else:
        if str(args) in list(spark_persistor.prompts_dict.keys()):
            del spark_persistor.prompts_dict[str(args)]
            spark_persistor.save()
            await spark_removeprompt.finish(f"成功删除预设{str(args)}")

        str_prompts = str()
        i = 1
        for key, value in spark_persistor.prompts_dict.items():
            str_prompts += f"{i}:{key}\n"
            i += 1
        replys = []
        if len(str_prompts) > 1000:
            pic = await md_to_pic(f"当前预设有：\n{str_prompts}\n输入 取消 或 算了 可以终止删除")
            pic = MessageSegment.image(pic)
            replys.append(await spark_removeprompt.send(pic))
        else:
            replys.append(
                await spark_removeprompt.send(
                    f"当前预设有：\n{str_prompts}\n输入 取消 或 算了 可以终止删除"
                )
            )

        replys.append(await spark_removeprompt.send("请输入要删除的预设名称\n输入取消 或 算了可以终止创建"))
        state["replys"] = replys


@spark_removeprompt.got("name")
async def __spark_removeprompt____(
    matcher:Matcher,bot: Bot, event: Event, state: T_State, infos: str = ArgStr("name")
):
    replys = state["replys"]
    if infos in ["取消", "算了"]:
        await delete_messages(bot, replys)
        await matcher.finish("终止删除")
    infos = infos.split(" ")
    if len(infos) != 1 or infos[0] not in spark_persistor.prompts_dict:
        replys.append(
            await matcher.send(
                "你输入的信息有误，请检查后重新输入\n输入取消 或 算了可以终止创建,终止后不会再发送此消息"
            )
        )
        await matcher.reject()
    if is_auto_prompt(infos[0]):
        prompt_no = is_auto_prompt(infos[0])
        await delete_messages(bot, replys)
        await matcher.finish(f"不能删除{prompt_no}自动创建机器人时指定的预设")

    del spark_persistor.prompts_dict[infos[0]]
    spark_persistor.save()
    await delete_messages(bot, replys)
    await matcher.finish(f"成功删除预设{infos[0]}")


spark_prompt_info = on_command("预设信息", aliases={"pf"}, priority=4, block=False)


@spark_prompt_info.handle()
async def spark_prompt_info_(
    matcher: Matcher, state: T_State, args: Message = CommandArg()
):
    replys = []
    if str(args) in list(spark_persistor.prompts_dict.keys()):
        prompt = spark_persistor.prompts_dict[str(args)]
        if len(prompt) > 1000:
            pic = await md_to_pic(prompt)
            await matcher.finish(MessageSegment.image(pic))
        await matcher.finish(f"预设内容为:{spark_persistor.prompts_dict[str(args)]}")
    else:
        replys.append(await matcher.send("请输入预设名称\n输入 取消 或 算了 可以终止查看"))
    state["replys"] = replys


@spark_prompt_info.got("prompt_nickname")
async def spark_prompt_info___(
    matcher: Matcher,
    bot: Bot,
    state: T_State,
    event: Event,
    infos: str = ArgStr("prompt_nickname"),
):
    replys = state["replys"]
    if str(infos) in ["取消", "算了"]:
        await delete_messages(bot, replys)
        await matcher.finish("取消查询")
    if str(infos) in list(spark_persistor.prompts_dict.keys()):
        try:
            await delete_messages(bot, replys)
        except:
            pass
        prompt = spark_persistor.prompts_dict[str(infos)]
        if len(prompt) > 1000:
            pic = await md_to_pic(prompt)
            await matcher.finish(MessageSegment.image(pic))
        await matcher.finish(f"预设内容为:{spark_persistor.prompts_dict[str(infos)]}")
    else:
        replys.append(
            await matcher.send(f"没有这个预设名称，请检查后重新输入\n输入 取消 或 算了 可以终止查询，终止后不会再发送此消息")
        )
        await matcher.reject()


spark_prompt_list = on_command("预设列表", aliases={"pl", "所有预设"}, priority=4, block=False)


@spark_prompt_list.handle()
async def spark_prompt_list__(matcher: Matcher):
    str_prompts = str("所有预设名称如下:  \n")
    i = 1
    for key, value in spark_persistor.prompts_dict.items():
        str_prompts += f"{i}:{key}\n"
        i += 1
    if len(str_prompts) > 1000:
        pic = await md_to_pic(str_prompts)
        await matcher.finish(MessageSegment.image(pic))
    await matcher.finish(str_prompts)


spark_list = on_command("bot列表", aliases={"botlist", "bl"}, priority=4, block=False)


@spark_list.handle()
async def spark_list___(event: Event, matcher: Matcher):
    current_userinfo, current_userdata = get_user_info_and_data(
        event,
    )
    bot_strs = []
    persistors = [
        gptweb_persistor,
        poe_persistor,
        claude_slack_persistor,
        spark_desk_persistor,
    ]
    bot_names = ["gpt_web", "poe", "claude_slack", "spark_desk"]

    for persistor, bot_name in zip(persistors, bot_names):
        try:
            bots = list(persistor.user_dict[current_userinfo]["all"].values())
            bot_str = f"{bot_name}机器人有:\n"
            for i, bot in enumerate(bots):
                bot_str += f"    {i+1}:{bot.nickname} "
                if bot_name == "poe":
                    bot_str += f"(模型:{bot.model}) "
                bot_str += f"(预设名:{bot.prompt_nickname})\n"
            bot_strs.append(bot_str)
        except:
            bot_strs.append(f"没有可用的{bot_name}机器人\n")

    msg = "可以直接/机器人名称 + 询问内容 来使用对应机器人\n比如/猫娘 在吗?\n所有机器人信息如下:\n\n" + "\n".join(bot_strs)
    if len(msg) > 1000:
        pic = await md_to_pic(msg)
        await matcher.finish(MessageSegment.image(pic))
    await matcher.finish(reply_out(event, msg))


spark_info = on_command("bot信息", aliases={"botinfo", "bf"}, priority=4, block=False)


@spark_info.handle()
async def spark_info__(event: Event, matcher: Matcher, args: Message = CommandArg()):
    if str(event.message).startswith("/bing"):
        await matcher.finish()
    try:
        nickname = str(args[0])
    except:
        await matcher.finish()
    try:
        botinfo, text, persistor = get_botinfo(nickname, event)
    except Exception as e:
        await matcher.finish(reply_out(event, str(e)))
    if len(text) > 1000:
        pic = await md_to_pic(text)
        await matcher.finish(reply_out(event, pic))
    await matcher.finish(reply_out(event, text))


spark_change_bot = on_command(
    "bot更改", aliases={"botchange", "bc"}, priority=4, block=False
)


@spark_change_bot.handle()
async def spark_change_bot__(
    event: Event, state: T_State, matcher: Matcher, args: Message = CommandArg()
):
    try:
        nickname = str(args[0])
    except:
        await matcher.finish()
    state["nickname"] = nickname
    wait_msg = []
    try:
        botinfo, text, persistor = get_botinfo(nickname, event)
        state["botinfo"] = botinfo
        state["persistor"] = persistor
    except Exception as e:
        await matcher.finish(reply_out(event, str(e)))
    if len(text) > 1000:
        pic = await md_to_pic(text)
        wait_msg.append(await matcher.send(reply_out(event, pic)))
    else:
        wait_msg.append(await matcher.send(reply_out(event, text)))
    wait_msg.append(
        await matcher.send(
            reply_out(
                event,
                "注意仅nickname,prompt,prompt_name,share(True,False)可以被修改\n\n请输入修改内容\n如:'nickname=猫娘'表示将机器人名称修改为猫娘\n如:'prompt=一个人工智能'表示将预设改为一个人工智能\n如:'nickname=小爱,prompt_nickname=小爱预设'表示将nickname修改为小爱,并将prompt_nickname修改为小爱预设",
            )
        )
    )
    state["wait_msg"] = wait_msg


@spark_change_bot.got("key")
async def spark_change_bot_(
    matcher: Matcher, bot: Bot, state: T_State, event: Event, infos: str = ArgStr("key")
):
    wait_msg = state["wait_msg"]
    botinfo = state["botinfo"]
    persistor = state["persistor"]
    nickname = state["nickname"]
    current_userinfo, current_userdata = get_user_info_and_data(
        event,
    )
    if infos in ["取消", "算了"]:
        await delete_messages(bot, wait_msg)
        await matcher.finish("取消更改")

    await delete_messages(bot, wait_msg)

    lst = infos.split(",")
    # 将列表中的每个元素按等号分隔成二元组，然后转成列表
    items = [list(item.split("=")) for item in lst]
    for item in items:
        key = item[0]
        value = item[1]
        if key == "nickname":
            if value == nickname:
                await matcher.send(reply_out(event, "更改后的nickname和原来的nickname相同"))
                continue
            if is_nickname(value, event):
                await matcher.send(reply_out(event, "已经有这个nickname的机器人了，不能重名"))
                continue
            setattr(botinfo, key, value)
            if nickname == list(persistor.user_dict[current_userinfo]["now"].keys())[0]:
                persistor.user_dict[current_userinfo]["now"][nickname] = botinfo
            del persistor.user_dict[current_userinfo]["all"][nickname]
            persistor.user_dict[current_userinfo]["all"][value] = botinfo
            nickname = value
            await matcher.send(reply_out(event, f"成功将机器人名称{key}修改为{value}"))

        elif key == "prompt":
            setattr(botinfo, key, value)
            persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
            if botinfo.source == "poe":
                if spark_persistor.poe_api_mode == 1:
                    page = await pwfw.new_page()
                    try:
                        await poe_change(page, botinfo.truename, value)
                        await matcher.send(
                            reply_out(
                                event, f"成功将{key}修改为你输入的预设内容\n再次使用该机器人时，请先清除对话(刷新对话)"
                            )
                        )
                    except Exception as e:
                        await matcher.send(
                            reply_out(event, f"更改poe预设出错:{e}，多次出错请联系机器人管理员")
                        )
                    await page.close()
                else:
                    try:
                        task = asyncio.create_task(run_poe_change(value, botinfo))
                        await asyncio.wait_for(task, 90)
                        await matcher.send(
                            reply_out(
                                event, f"成功将{key}修改为你输入的预设内容\n再次使用该机器人时，请先清除对话(刷新对话)"
                            )
                        )
                    except Exception as e:
                        await matcher.send(
                            reply_out(event, f"更改poe预设出错:{e}，多次出错请联系机器人管理员")
                        )
            else:
                setattr(botinfo, key, value)
                persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
                await matcher.send(
                    reply_out(event, f"成功将{key}修改为你输入的预设内容\n再次使用该机器人时，请先清除对话(刷新对话)")
                )
        elif key == "prompt_nickname":
            setattr(botinfo, key, value)
            persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
            await matcher.send(reply_out(event, f"成功将{key}修改为{value}"))
        elif key == "share":
            if value == "False":
                value = False
            elif value == "True":
                value = True
            else:
                await matcher.send(reply_out(event, f"share只能被设置被True或False"))
            setattr(botinfo, key, value)
            persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
            await matcher.send(reply_out(event, f"成功将{key}修改为{value}"))
        else:
            await matcher.send(reply_out(event, f"{key}不存在或不可被修改。"))
        persistor.save()
    await matcher.finish()


spark_share_list = on_command("sbl", aliases={"sharebotlist"}, priority=4, block=False)


@spark_share_list.handle()
async def spark_share_list___(event: Event, matcher: Matcher):
    current_userinfo, current_userdata = get_public_info_data()
    bot_strs = []
    persistors = [gptweb_persistor, poe_persistor, claude_slack_persistor]
    bot_names = ["gpt_web", "poe", "claude_slack"]

    for persistor, bot_name in zip(persistors, bot_names):
        try:
            bots = list(persistor.user_dict[current_userinfo]["all"].values())
            bot_str = f"{bot_name}机器人有:\n"
            for i, bot in enumerate(bots):
                bot_str += f"    {i+1}:{bot.nickname} "
                if bot_name == "poe":
                    bot_str += f"(模型:{bot.model}) "
                bot_str += f"(预设名:{bot.prompt_nickname})\n"
            bot_strs.append(bot_str)
        except:
            bot_strs.append(f"没有可用的{bot_name}机器人\n")

    msg = "注意共享机器人使用时应在名前加'共享'或'share',\n比如 /共享猫娘 在吗？\n所有机器人信息如下:\n\n" + "\n".join(
        bot_strs
    )
    if len(msg) > 1000:
        pic = await md_to_pic(str(msg))
        await matcher.finish(MessageSegment.image(pic))
    await matcher.finish(reply_out(event, msg))


spark_share_remove = on_command(
    "sbr", aliases={"sharebotremove"}, priority=4, block=False
)


@spark_share_remove.handle()
async def spark_share_remove__(
    event: Event, matcher: Matcher, args: Message = CommandArg()
):
    if str(event.user_id) not in spark_persistor.superusers:
        await matcher.finish("你不是管理员，没有权限")
    if str(args):
        nickname = str(args)
    else:
        await matcher.finish()
    if not is_public_nickname(nickname):
        await matcher.finish(reply_out(event, "没有这个共享机器人"))
    public_user_info, public_user_data = get_public_info_data()
    try:
        botinfo, text, persistor = get_public_botinfo(nickname)
    except Exception as e:
        await matcher.finish(reply_out(event, str(e)))
    del persistor.user_dict[public_user_info]["all"][nickname]
    await matcher.finish(reply_out(event, f"成功删除共享机器人:{nickname}"))


spark_change_share_bot = on_command(
    "sbc", aliases={"sharebotchange"}, priority=4, block=False
)


@spark_change_share_bot.handle()
async def spark_change_share_bot__(
    event: Event, state: T_State, matcher: Matcher, args: Message = CommandArg()
):
    if str(event.user_id) not in spark_persistor.superusers:
        await matcher.finish("你不是管理员，没有权限")
    try:
        nickname = str(args[0])
    except:
        await matcher.finish()
    state["nickname"] = nickname
    wait_msg = []
    try:
        botinfo, text, persistor = get_public_botinfo(nickname)
        state["botinfo"] = botinfo
        state["persistor"] = persistor
    except Exception as e:
        await matcher.finish(reply_out(event, str(e)))
    if len(text) > 1000:
        pic = await md_to_pic(text)
        wait_msg.append(await matcher.send(reply_out(event, pic)))
    else:
        wait_msg.append(await matcher.send(reply_out(event, text)))
    wait_msg.append(
        await matcher.send(
            reply_out(
                event,
                "注意仅nickname,prompt,prompt_name可以被修改\n\n请输入修改内容\n如:'nickname=猫娘'表示将机器人名称修改为猫娘\n如:'prompt=一个人工智能'表示将预设改为一个人工智能\n如:'nickname=小爱,prompt_nickname=小爱预设'表示将nickname修改为小爱,并将prompt_nickname修改为小爱预设",
            )
        )
    )
    state["wait_msg"] = wait_msg


@spark_change_share_bot.got("key")
async def spark_change_share_bot_(
    matcher: Matcher, bot: Bot, state: T_State, event: Event, infos: str = ArgStr("key")
):
    wait_msg = state["wait_msg"]
    botinfo = state["botinfo"]
    persistor = state["persistor"]
    nickname = state["nickname"]
    current_userinfo, current_userdata = get_public_info_data()
    if infos in ["取消", "算了"]:
        await delete_messages(bot, wait_msg)
        await matcher.finish("取消更改")

    await delete_messages(bot, wait_msg)

    lst = infos.split(",")
    # 将列表中的每个元素按等号分隔成二元组，然后转成列表
    items = [list(item.split("=")) for item in lst]
    for item in items:
        key = item[0]
        value = item[1]
        if key == "nickname":
            if value == nickname:
                await matcher.send("更改后的nickname和原来的nickname相同")
                continue
            if is_public_nickname(value):
                await matcher.send("已经有这个nickname的机器人了，不能重名")
                continue
            setattr(botinfo, key, value)
            if nickname == list(persistor.user_dict[current_userinfo]["now"].keys())[0]:
                persistor.user_dict[current_userinfo]["now"][nickname] = botinfo
            del persistor.user_dict[current_userinfo]["all"][nickname]
            persistor.user_dict[current_userinfo]["all"][value] = botinfo
            nickname = value
            await matcher.send(f"成功将机器人名称{key}修改为{value}")

        elif key == "prompt":
            setattr(botinfo, key, value)
            persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
            if botinfo.source == "poe":
                if spark_persistor.poe_api_mode == 1:
                    page = await pwfw.new_page()
                    try:
                        await poe_change(page, botinfo.truename, value)
                        await matcher.send(
                            f"成功将{key}修改为你输入的预设内容\n再次使用该机器人时，请先清除对话(刷新对话)"
                        )
                    except Exception as e:
                        await matcher.send(f"更改poe预设出错:{e}，多次出错请联系机器人管理员")
                    await page.close()
                else:
                    try:
                        task = asyncio.create_task(run_poe_change(value, botinfo))
                        await asyncio.wait_for(task, 90)
                        await matcher.send(
                            f"成功预设内容将{key}修改为你输入的预设内容\n再次使用该机器人时，请先清除对话(刷新对话)"
                        )
                    except Exception as e:
                        await matcher.send(f"更改poe预设出错:{e}，多次出错请联系机器人管理员")
            else:
                setattr(botinfo, key, value)
                persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
                await matcher.send(f"成功将{key}修改为你输入的预设内容\n再次使用该机器人时，请先清除对话(刷新对话)")
        elif key == "prompt_nickname":
            setattr(botinfo, key, value)
            persistor.user_dict[current_userinfo]["all"][nickname] = botinfo
            await matcher.send(f"成功将{key}修改为{value}")
        else:
            await matcher.send(f"{key}不存在或不可被修改。")
        persistor.save()
    await matcher.finish()


# test = on_command("md2pic", priority=4, block=False)

# @test.handle()
# async def test_(
#     matcher: Matcher,
#     event: Event,
#     state: T_State,
#     args: Message = CommandArg(),
# ):
#     text = str(args[0])
#     pic = await md_to_pic(text)
#     await matcher.finish(reply_out(event, pic))
