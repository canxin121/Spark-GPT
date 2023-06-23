import json
from pathlib import Path
from nonebot.exception import ActionFailed, NetworkError
from nonebot import logger
from nonebot.plugin import on_command, on_message
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
from ImageGen import ImageGenAsync
from .newbing_func import is_useable, sendmsg
from .config import newbing_persistor, newbingtemper, set_userdata
from .newbing_api import Newbing_bot
from EdgeGPT import Chatbot, ConversationStyle
from ..common.render.render import md_to_pic
from ..common.common_func import delete_messages, reply_out

sourcepath = Path(__file__).parent.parent / "source"
logger.info("开始加载Newbing")
user_data_dict = newbingtemper.user_data_dict


#############################################################
async def _is_chat_(event: MessageEvent, bot: Bot):
    if is_useable(event):
        try:
            current_userinfo, current_userdata = set_userdata(
                event=event, user_data_dict=user_data_dict
            )
        except:
            return False
        if bool(event.reply):
            if (
                str(event.reply.sender.user_id) == bot.self_id
                and event.reply.message_id == current_userdata.last_reply_message_id
            ):
                raw_message = str(event.message)
                if not raw_message:
                    return False
                else:
                    return raw_message, current_userinfo, current_userdata
            else:
                return False
        elif str(event.message).startswith(("/bing", "/b")) and not str(
            event.message
        ).startswith(
            (
                "/bc",
                "/bing切换",
                "/bingdraw",
                "/bd",
                "/bing绘图",
                "/bing画图",
                "/binghelp",
                "/bing帮助",
                "/bh",
                "/bl",
                "/bot",
                "/bard",
                "/bc",
                "/bf",
                "/bs",
            )
        ):
            raw_message = (
                str(event.message)
                .replace("/bing ", "")
                .replace("/bing", "")
                .replace("/b ", "")
                .replace("/b", "")
            )
            if not raw_message:
                return False
            else:
                return raw_message, current_userinfo, current_userdata
    else:
        return False


newbing_chat = on_message(priority=1, block=False)


@newbing_chat.handle()
async def __newbing_chat__(matcher: Matcher, event: Event, bot: Bot):
    temp_tuple = await _is_chat_(event, bot)
    if temp_tuple == False or not temp_tuple:
        await matcher.finish()
    else:
        if isinstance(temp_tuple, tuple):
            raw_message, current_userinfo, current_userdata = temp_tuple
        elif isinstance(temp_tuple, str):
            await matcher.finish(reply_out(event, f"出错了:{temp_tuple}"))

    if raw_message in [
        "清除对话",
        "清空对话",
        "清除历史",
        "清空历史",
        "清除记录",
        "清空记录",
        "清空历史对话",
        "刷新对话",
    ]:
        try:
            async with Newbing_bot(event) as newbing_bot:
                await newbing_bot.refresh()
            await matcher.finish(reply_out(event, "成功刷新对话"))
        except ActionFailed:
            await matcher.finish(reply_out(event, "刷新对话失败"))
    if (
        len(raw_message) == 1
        and raw_message in ["1", "2", "3"]
        and current_userdata.last_suggests
    ):
        raw_message = current_userdata.last_suggests[int(raw_message) - 1]
    if current_userdata.is_waiting:
        await matcher.finish(reply_out(event, "你有一个对话进行中，请等结束后再继续询问"))

    try:
        wait_msg = await matcher.send(reply_out(event, "正在思考，请稍等"))
        current_userdata.is_waiting = True
        async with Newbing_bot(event) as newbing_bot:
            raw_json = await newbing_bot.ask(raw_message)
            # print(raw_json)
        current_userdata.is_waiting = False
    except Exception as e:
        logger.error(str(e))
        current_userdata.is_waiting = False
        await bot.delete_msg(message_id=wait_msg["message_id"])
        await matcher.send(reply_out(event, f"出错喽:{str(e)}，多次失败请尝试刷新对话"))
        await matcher.finish()
    try:
        value = raw_json["item"]["result"]["value"]
    except Exception as e:
        logger.error(str(e))
        current_userdata.is_waiting = False
        await bot.delete_msg(message_id=wait_msg["message_id"])
        await matcher.send(reply_out(event, f"出错喽:{str(e)}，多次失败请尝试刷新对话"))
        await matcher.finish()
    if value != "Success":
        if value == "Throttled":
            await matcher.finish(reply_out(event, "该账号cookie问答次数已达到今日上限"))
        elif value == "InvalidSession":
            await matcher.finish(reply_out(event, "无效会话捏"))
        else:
            await matcher.finish(reply_out(event, f"出错喽:{value}，多次失败请尝试刷新对话"))

    reply = ""
    last_num = len(raw_json["item"]["messages"])-1
    try:
        max_num = raw_json["item"]["throttling"]["maxNumUserMessagesInConversation"]
        now_num = raw_json["item"]["throttling"]["numUserMessagesInConversation"]
        if "messageType" in raw_json["item"]["messages"][last_num]:
            last_num -= 1
        reply = raw_json["item"]["messages"][last_num]["text"]
        reply = (
            reply.replace("&#91;", "[")
            .replace("&#93;", "]")
            .replace("[^", "[")
            .replace("^]", "]")
        )
    except:
        pass

    try:
        is_offense = raw_json["item"]["messages"][0]["offense"]

        if is_offense == "Offensive" and not reply:
            await matcher.finish(reply_out(event, "你的询问太冒犯了,newbing拒绝回答"))
        if "hiddenText" in raw_json["item"]["messages"][last_num] and not reply:
            await matcher.finish(reply_out(event, "你的询问太敏感了,newbing拒绝回答"))
    except FinishedException:
        await bot.delete_msg(message_id=wait_msg["message_id"])
        raise

    ##纯文本正文部分
    msg_text = reply + "\n"

    # 尝试解析图片或其他资源
    try:
        forward_msg = None
        html_resource = ""
        image_sources = [
            a["seeMoreUrl"]
            for a in raw_json["item"]["messages"][last_num]["sourceAttributions"]
            if "seeMoreUrl" in a
        ]
        image_names = [
            a["providerDisplayName"]
            for a in raw_json["item"]["messages"][last_num]["sourceAttributions"]
            if "providerDisplayName" in a
        ]
        image_links = [
            a["imageLink"]
            for a in raw_json["item"]["messages"][last_num]["sourceAttributions"]
            if "imageLink" in a
        ]
        for i in range(len(image_sources)):
            source_link = image_sources[i]
            display_name = image_names[i]
            each_msg = MessageSegment.text(f"[{i+1}] {display_name}:\n{source_link}\n")
            html_each_msg = f'[{i+1}]:<a href="{source_link}">{display_name}</a>\n'
            if len(image_links) - i > 0:
                image_link = image_links[i]
                each_msg += MessageSegment.image(image_link)
                html_each_msg += f"<img src={image_link} alt={i+1}>\n"
            forward_msg += MessageSegment.node_custom(
                user_id=current_userdata.sender.user_id,
                nickname=current_userdata.sender.user_name,
                content=each_msg,
            )
            html_resource += html_each_msg
    except:
        pass

    ##处理建议回复
    if newbing_persistor.suggest_able == "True":
        suggest_str = "\n建议回复:\n"
        try:
            suggests = [
                raw_json["item"]["messages"][last_num]["suggestedResponses"][i]["text"]
                for i in range(
                    len(raw_json["item"]["messages"][last_num]["suggestedResponses"])
                )
            ]
            suggest_str += "\n".join(
                [f"{i+1}. {suggestion}  " for i, suggestion in enumerate(suggests)]
            )
        except:
            suggests = []
            pass
    else:
        suggests = []
        suggest_str = ""

    ##加上回复上限
    fianl_msg = f"\n回复上限:{now_num}/{max_num}  "
    is_forward = False
    if (
        newbing_persistor.pic_able == None
        and len(msg_text + html_resource + suggest_str + fianl_msg)
        >= newbing_persistor.num_limit
    ) or newbing_persistor.pic_able == "True":
        msg = msg_text + html_resource + suggest_str + fianl_msg
    else:
        msg = msg_text + suggest_str + fianl_msg
        is_forward = True
    current_userdata.is_waiting = False
    await bot.delete_msg(message_id=wait_msg["message_id"])
    reply_msgid_container = await sendmsg(msg, matcher, event)

    current_userdata.last_reply_message_id = reply_msgid_container["message_id"]
    current_userdata.last_suggests = suggests

    if forward_msg and is_forward:
        try:
            # 尝试合并转发
            if forward_msg and event.message_type == "group":
                reply_msgid_container = await bot.send_group_forward_msg(
                    group_id=event.group_id, messages=forward_msg
                )
            elif forward_msg and event.message_type == "private":
                reply_msgid_container = await bot.send_private_forward_msg(
                    user_id=event.user_id, messages=forward_msg
                )
            current_userdata.last_reply_message_id = reply_msgid_container["message_id"]
        except:
            pass

    if now_num == max_num:
        await matcher.send(reply_out(event, "已达到单次对话上限，自动为您刷新对话"))
        try:
            async with Newbing_bot(event) as newbing_bot:
                await newbing_bot.refresh()
        except Exception as e:
            await matcher.finish(reply_out(event, f"自动刷新出错:{e}"))

    await matcher.finish()


newbing_change_mode = on_command(
    "bs", aliases={"bingswitch", "bing切换"}, priority=1, block=False
)


@newbing_change_mode.handle()
async def __newbing_change_mode__(
    matcher: Matcher,
    state: T_State,
    event: MessageEvent,
    bot: Bot,
    args: Message = CommandArg(),
):
    try:
        current_userinfo, current_userdata = set_userdata(
            event=event, user_data_dict=user_data_dict
        )
    except:
        await matcher.finish()
    if args and len(args) == 1 and str(args) in ["1", "2", "3"]:
        current_userdata.chatmode = str(args)
        if str(args) == "1":
            style = "creative 创造力模式"
        elif str(args) == "2":
            style = "balanced 均衡模式"
        else:
            style = "precise 精确模式"
        await matcher.finish(reply_out(event, f"已切换为: {style}"))
    msg = (
        "请输入模式前索引数字\n1:creative 创造力模式\n2:balanced 均衡模式\n3:precise 精确模式\n输入 取消或算了 可以终止切换"
    )
    replys = []
    replys.append(await matcher.send(reply_out(event, msg)))
    state["replys"] = replys
    state["current_userdata"] = current_userdata


@newbing_change_mode.got("mode")
async def newbing_change_mode__(
    matcher: Matcher,
    state: T_State,
    event: MessageEvent,
    bot: Bot,
    infos: str = ArgStr("mode"),
):
    current_userdata = state["current_userdata"]
    replys = state["replys"]
    if str(infos):
        mode = str(infos)
    else:
        await matcher.finish()
    if mode and mode in ["取消", "算了"]:
        await matcher.send(reply_out(event, "取消切换"))
        await delete_messages(bot, replys)
        await matcher.finish()
    if mode and len(mode) == 1 and mode in ["1", "2", "3"]:
        current_userdata.chatmode = mode
        if mode == "1":
            style = "creative 创造力模式"
        elif mode == "2":
            style = "balanced 均衡模式"
        else:
            style = "precise 精确模式"
        await matcher.send(reply_out(event, f"已切换为: {style}"))
        await delete_messages(bot, replys)
        await matcher.finish()
    else:
        replys.append(
            await matcher.send(
                reply_out(event, f"你输入的数字有误，请重新输入\n输入算了 或 取消 可以终止切换,终止后不会再发送本条消息")
            )
        )
        await matcher.reject()


bing_draw = on_command(
    "bingdraw", aliases={"bd", "bing绘图", "bing画画"}, priority=1, block=False
)


@bing_draw.handle()
async def __newbing_change_mode__(
    matcher: Matcher,
    state: T_State,
    event: MessageEvent,
    bot: Bot,
    args: Message = CommandArg(),
):
    try:
        current_userinfo, current_userdata = set_userdata(
            event=event, user_data_dict=user_data_dict
        )
    except:
        await matcher.finish()
    if not args[0]:
        await matcher.finish()
    else:
        prompt = str(args[0])

    if current_userdata.is_waiting:
        await matcher.finish(reply_out(event, f"你有一个对话进行中，请等结束后再继续询问"))
    try:
        with open(newbing_persistor.cookie_path_, encoding="utf-8") as file:
            cookie_json = json.load(file)
            for cookie in cookie_json:
                if cookie.get("name") == "_U":
                    auth_cookie = cookie.get("value")
                    break
            else:
                logger.warning("newbing的cookie内容有误,无法使用，跳过")
                await matcher.finish()
    except FileNotFoundError:
        logger.warning("newbing cookie未配置,无法使用，跳过")
        await matcher.finish()
    current_userdata.is_waiting = True
    from pathlib import Path

    wait_msg = await matcher.send(reply_out(event, "正在绘制，请稍等"))
    try:
        async with ImageGenAsync(auth_cookie) as image_generator:
            image_links = await image_generator.get_images(prompt)
            max_retry = 3  # 最大重试次数
            retry_count = 0  # 当前重试次数
            if newbing_persistor.predownload == "True":
                while retry_count < max_retry:
                    try:
                        temp_path = Path("./data/spark_gpt/temp/")
                        jpeg_files = list(temp_path.glob("*.jpeg"))
                        # 删除所有JPEG格式的文件
                        for file_path in jpeg_files:
                            file_path.unlink()

                        await image_generator.save_images(image_links, temp_path)
                        break  # 如果保存成功，则跳出循环
                    except Exception as e:
                        retry_count += 1
                        print(f"Error occurred while saving images: {e}")
                        if retry_count == max_retry:
                            # 如果达到最大重试次数还是保存失败，则抛出异常
                            await matcher.finish(
                                reply_out(event, f"下载图片出错，多次出错请联系机器人主人")
                            )
    except Exception as e:
        current_userdata.is_waiting = False
        await matcher.finish(reply_out(event, f"生成图片出错:{str(e)}，多次出错请联系机器人主人"))
    try:
        await bot.delete_msg(message_id=wait_msg["message_id"])
    except:
        pass

    current_userdata.is_waiting = False

    try:
        forward_msg = MessageSegment.node_custom(
            user_id=current_userdata.sender.user_id,
            nickname=current_userdata.sender.user_name,
            content=MessageSegment.text("绘图结果如下:\n"),
        )
        image_msg = MessageSegment.text("绘图结果如下:\n")
        for i in range(4):
            if newbing_persistor.predownload == "True":
                image_msg += MessageSegment.image(Path(temp_path / f"{i}.jpeg"))
                forward_msg += MessageSegment.node_custom(
                    user_id=current_userdata.sender.user_id,
                    nickname=current_userdata.sender.user_name,
                    content=MessageSegment.image(Path(temp_path / f"{i}.jpeg")),
                )
            else:
                image_msg += MessageSegment.image(image_links[i])
                forward_msg += MessageSegment.node_custom(
                    user_id=current_userdata.sender.user_id,
                    nickname=current_userdata.sender.user_name,
                    content=MessageSegment.image(image_links[i]),
                )

    except Exception as e:
        await matcher.finish(reply_out(event, f"发送图片出错: {e}"))

    if newbing_persistor.forward == "True":
        try:
            # 尝试合并转发
            if forward_msg and event.message_type == "group":
                await bot.send_group_forward_msg(
                    group_id=event.group_id, messages=forward_msg
                )
            elif forward_msg and event.message_type == "private":
                await bot.send_private_forward_msg(
                    user_id=event.user_id, messages=forward_msg
                )
        except:
            await matcher.finish(reply_out(event, image_msg))
    else:
        await matcher.finish(reply_out(event, image_msg))


######################################################
newbing_help = on_command("binghelp", aliases={"bing帮助", "bh"}, priority=4, block=False)


@newbing_help.handle()
async def __newbing_help__(matcher: Matcher):
    if not is_useable:
        await matcher.finish()
    msg = """
# spark-gpt NewBing使用说明

- 机器人对每个人都是相互独立的。

- !!! 以下命令前面全部要加 '/' !!!  

## 对话命令
- 支持以下特性：可以通过对话 (清除/清空)(对话/历史)或"刷新对话"或"清空历史对话"来开启另一个新对话  
- 对话一次后，就可以直接回复机器人给你的最后的回复来进行连续对话  
- 可以通过建议回复的数字索引来使用建议回复  

| 命令 | 描述 |
| --- | --- |
| `/bing / b + 内容` | 对话功能|

## 切换对话模式命令

| 命令 | 描述 |
| --- | --- |
| `/bs / bingswitch / bing切换 (+ 数字)` | 切换对话模式，支持以下三种模式：1. 创造力模式；2. 均衡模式；3. 精确模式。 |

## 画图命令

| 命令 | 描述 |
| --- | --- |
| `/bingdraw / bd / bing绘图(bing画图) + 要画的东西(中文/英文)` | Dall-e画图功能，可以画出指定的中文或英文内容。 |"""
    # pic = await md_to_pic(msg)
    # await matcher.send(MessageSegment.image(pic))
    await matcher.send(
        MessageSegment.image(Path(sourcepath / Path("demo(3).png")).absolute())
    )
    await matcher.finish()
