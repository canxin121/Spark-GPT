from nonebot.plugin import on_command
from nonebot.params import ArgStr
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Event, Message
from nonebot.params import ArgStr, CommandArg
from .render.render import md_to_pic
from .common_func import reply_out
from .config import spark_persistor, get_user_info_and_data
from .common_func import is_auto_prompt
from ..chatgpt_web.config import gptweb_persistor
from ..poe.config import poe_persistor
from ..claude_slack.config import claude_slack_persistor

spark_addprompt = on_command("添加预设", aliases={"ap"}, priority=4, block=False)


@spark_addprompt.handle()
async def __spark_addprompt__(matcher: Matcher, event: Event):
    global spark_persistor
    user_id = str(event.user_id)
    if user_id not in spark_persistor.superusers:
        await spark_addprompt.finish("你不是管理员哦")


@spark_addprompt.got("name", prompt="请输入预设名称\n输入取消 或 算了可以终止创建")
async def __spark_addprompt____(
    event: Event, state: T_State, infos: str = ArgStr("name")
):
    global spark_persistor
    if infos in ["取消", "算了"]:
        await spark_addprompt.finish("终止添加")
    infos = infos.split(" ")
    if len(infos) != 1:
        await spark_addprompt.reject("你输入的信息有误，请检查后重新输入")
    state["key"] = infos[0]


@spark_addprompt.got("prompt", prompt="请输入预设\n输入取消 或 算了可以终止创建")
async def __spark_addprompt____(
    event: Event, state: T_State, infos: str = ArgStr("prompt")
):
    global spark_persistor
    if infos in ["取消", "算了"]:
        await spark_addprompt.finish("终止添加")
    infos = infos.split(" ")
    name = state["key"]
    prompt = infos[0]
    # # 将更新后的字典写回到JSON文件中
    spark_persistor.prompts_dict[name] = prompt
    spark_persistor.save()
    await spark_addprompt.finish("成功添加prompt")


######################################################
spark_removeprompt = on_command("删除预设", aliases={"rp"}, priority=4, block=False)


@spark_removeprompt.handle()
async def __spark_removeprompt__(event: Event):
    global spark_persistor
    user_id = str(event.user_id)
    if user_id not in spark_persistor.superusers:
        await spark_removeprompt.finish("你不是管理员哦")
    else:
        str_prompts = str()
        i = 1
        for key, value in spark_persistor.prompts_dict.items():
            str_prompts += f"************************\n{i}:预设名称：{key}\n预设内容：{value}\n"
            i += 1
        await spark_removeprompt.send(f"当前预设有：\n{str_prompts}")


@spark_removeprompt.got("name", prompt="请输入要删除的预设名称\n输入取消 或 算了可以终止创建")
async def __spark_removeprompt____(event: Event, infos: str = ArgStr("name")):
    if infos in ["取消", "算了"]:
        await spark_removeprompt.finish("终止删除")
    infos = infos.split(" ")
    if len(infos) != 1 or infos[0] not in spark_persistor.prompts_dict:
        await spark_removeprompt.reject("你输入的信息有误，请检查后重新输入")
    if is_auto_prompt(infos[0]):
        prompt_no = is_auto_prompt(infos[0])
        await spark_removeprompt.finish(f"不能删除{prompt_no}自动创建机器人时指定的预设")

    del spark_persistor.prompts_dict[infos[0]]
    spark_persistor.save()
    await spark_removeprompt.finish(f"成功删除预设{infos[0]}")


spark_removeprompt = on_command(
    "bot列表", aliases={"botlist", "bl"}, priority=4, block=False
)


@spark_removeprompt.handle()
async def __spark_removeprompt__(event: Event, matcher: Matcher):
    current_userinfo, current_userdata = get_user_info_and_data(
        event,
    )
    try:
        gw_bots = list(gptweb_persistor.user_dict[current_userinfo]["all"].keys())
        gw_bot_str = "gpt_web机器人有:\n"
        for i in range(len(gw_bots)):
            gw_bot_str += f"    {i+1}:{gw_bots[i]}\n"
    except:
        gw_bot_str = "没有可用的gpt_web机器人\n"
    try:
        poe_bots = list(poe_persistor.user_dict[current_userinfo]["all"].keys())
        poe_bot_str = "poe机器人有:\n"
        for i in range(len(poe_bots)):
            poe_bot_str += f"    {i+1}:{poe_bots[i]}\n"
    except:
        poe_bot_str = "没有可用的poe机器人\n"
    try:
        claude_slack_bots = list(
            claude_slack_persistor.user_dict[current_userinfo]["all"].keys()
        )
        claude_slack_bot_str = "claude_slack机器人有:\n"
        for i in range(len(claude_slack_bots)):
            claude_slack_bot_str += f"    {i+1}:{claude_slack_bots[i]}\n"
    except:
        claude_slack_bot_str = "没有可用的poe机器人\n"
    msg = "所有机器人信息如下:\n\n" + gw_bot_str + poe_bot_str + claude_slack_bot_str
    await matcher.finish(reply_out(event, msg))


test = on_command("md2pic", priority=4, block=False)


@test.handle()
async def test_(
    matcher: Matcher,
    event: Event,
    state: T_State,
    args: Message = CommandArg(),
):
    text = str(args[0])
    pic = await md_to_pic(text)
    await matcher.finish(reply_out(event, pic))
