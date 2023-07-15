import asyncio
import threading
from pathlib import Path

import nonebot
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from ..config import config
from ..prefix_data import prefixes
from ..prompt_data import prompts
from ...chatbot.load_config import load_config

get_config = nonebot.get_driver().config

HOST = get_config.spark_host if hasattr(get_config, "spark_host") else "127.0.0.1"

PORT = int(get_config.spark_port) if hasattr(get_config, "spark_port") else 8666

PICABLE = "是否开启以图片形式进行回复(True为是,False为否,Auto为当字数在num_limit以上是自动转化成图片回复,否则则回复文本原文)"
URLABLE = "是否在以图片形式回复的后面添加文本原文的剪切板链接"
NUM_LIMIT = "在pic_able设置为Auto时的字数限制"

app = FastAPI()
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

COMMENTS = (
    {
        "总控配置": {
            "superusers": "填写你的用户名组成的列表,格式示例['1234567890','2876391827'],注意是通过使用命令 /用户信息来获取的通用用户名,而不是qq或tg用户名",
            "pic_able": PICABLE,
            "url_able": URLABLE,
            "wait_msg_able": '是否发送"正在思考\刷新,请稍等",默认True为发送,False为不发送',
            "num_limit": NUM_LIMIT,
            "private_command": "私人的bot的控制和使用前缀,默认‘/’",
            "public_command": "公用的bot的控制和使用前缀,默认‘.’",
            "pic_width": "文字转图片的宽度",
        },
        "Newbing配置": {
            "cookie": "Newbing的cookie json,获取方法为登录微软账号并打开到bing聊天界面,使用浏览器扩展 cookie editor将cookie导出为json格式并粘贴到此处",
            "proxy": "EdgeGPT的代理地址,请按照协议://地址:端口的格式填写",
            "wss_link": "EdgeGPT的wss_link地址,如果无法使用,可以自建cf代理,详细教程https://canxin121.github.io/docs/docs/Spark_GPT.html#QA中的第一个",
        },
        "Spark Desk配置": {
            "cookie": "讯飞星火语言模型的cookie,获取方法为使用抓包工具如fiddler在与星火模型聊天时抓包,在包含chat关键字的连接的 请求头 中提取cookie",
            "fd": "讯飞星火语言模型的fd,获取方法为使用抓包工具如fiddler在与星火模型聊天时抓包,在包含chat关键字的连接的 请求体 中提取fd",
            "GtToken": "讯飞星火语言模型的GtToken,获取方法为使用抓包工具如fiddler在与星火模型聊天时抓包,在包含chat关键字的连接的 请求体 中提取Gttoken",
            "sid": "讯飞星火语言模型的sid,获取方法为使用抓包工具如fiddler在与星火模型聊天时抓包,在包含chat关键字的连接的 响应体末尾 中提取sid(格式示例是cht000d1737@dx1886666eb4ab894540)",
        },
        "Chat GPT web配置": {
            "session token": "ChatGPT网页版的session token,获取方法为在chatgpt网页版按F12调出开发者工具,在应用程序->cookie中的复制__Secure-next-auth.session-token项对应的值填写到此处",
            "model": "ChatGPT网页版的模型,默认text-davinci-002-render-sha为gpt3.5",
            "proxy": "访问ChatGPT网页版代理地址使用的代理",
            "api_url": "ChatGPT网页版使用的代理网址,如果默认网址失效可以更改为可用的代理网址",
        },
        "Claude Slack配置": {
            "slack_user_token": '首先参照 "https://ikechan8370.com/archives/chatgpt-plugin-for-yunzaipei-zhi-slack-claude"进行配置,获取到其中的(OAuth & Permissions中)User OAuth Token(xoxp-5258801~~,注意是xoxp不是xoxb)作为slack_user_token(必填)',
            "claude_id": 'claude_id获取:首先将claude加入到你的slack中来,参考"https://blog.csdn.net/Ping_lz/article/details/130329751",并点击应用中的claude,点击聊天界面上方的claude的头像,复制其中的成员id作为claude_id(必填),比如U057LPZPPSL。',
            "channel_id": "进入slack聊天界面,选择(创建)一个专用的频道,将claude拉进这个频道。此时记下这个频道的网址中的channel_id(必填)(比如在这个链接中 https://app.slack.com/client/T057LPK0SP2/C0579MZR3LH/thread/C0579MZR3LH-1683734208.221819 ,channel_id是C0579MZR3LH,及thread前面的两个/中的内容)",
        },
        "Claude Ai配置": {
            "cookie": "获取方式为打开https://claude.ai和开发者工具中的网络,和claude进行对话,并在append_message的请求中获取请求头中的cookie",
            "organization_uuid": "获取方式为登陆后打开https://claude.ai/api/organizations,并复制uuid一项的值,填写在此处",
            "proxy": "访问POE官网时使用的代理链接,请按照协议://地址:端口的格式填写",
        },
        "Poe配置": {
            "cookie": "获取方式为打开https://poe.com/,登录后F12打开开发者工具,在应用程序->cookie中复制p-b项的值,如l_recO0QgugqEyfgMbBc-g%3D%3D",
            "proxy": "访问POE官网时使用的代理链接,请按照协议://地址:端口的格式填写",
        },
        "Bard配置": {
            "__Secure-1PSID": "获取方式:打开Bard网页,打开开发者工具中的应用程序,选择其中的cookie,并且复制其中的__Secure-1PSID一项的值复制到这里",
            "proxy": "访问Bard官网时使用的代理链接,请按照协议://地址:端口的格式填写",
        },
        "通义千问配置": {
            "cookie": "获取方法为打开通义千问聊天界面,F12打开开发者工具的网络界面,提取其中的heartbeat请求的cookie的值",
            "XSRF_TOKEN": "获取方法为获取方法为打开通义千问聊天界面,F12打开开发者工具的应用程序界面,选择左侧cookie,提取其中的XSRF_TOKEN的值",
        },
    },
)

DESCRIPTIONS = {
    "总控配置": "总的配置控制",
    "Newbing配置": "Newbing聊天机器人的配置(留空则默认从总控配置读取)",
    "Spark Desk配置": "Spark Desk聊天机器人的配置(留空则默认从总控配置读取)",
    "Chat GPT web配置": "Chat GPT web聊天机器人的配置(留空则默认从总控配置读取)",
    "Claude Slack配置": "Claude Slack聊天机器人的配置(留空则默认从总控配置读取)",
    "Claude Ai配置": "Claude Ai聊天机器人的配置(留空则默认从总控配置读取)",
    "Poe配置": "Poe聊天机器人的配置(留空则默认从总控配置读取)",
    "Bard配置": "Google Bard聊天机器人的配置(留空则默认从总控配置读取)",
    "通义千问配置": "通义千问聊天机器人的配置(留空则默认从总控配置读取)",
}
ABLE = True


class Fastapp:
    @app.get("/")
    async def index(request: Request):
        if not ABLE:
            return "已关闭webui,禁止访问"
        return TEMPLATES.TemplateResponse("index.html", {"request": request})

    @app.get("/config")
    @app.get("/config/{dict_name}")
    @app.post("/config")
    @app.post("/config/{dict_name}")
    async def save_edit_config(request: Request, dict_name: str = ""):
        if not ABLE:
            return "已关闭webui,禁止访问"
        form = await request.form()
        if not dict_name:
            dict_name = list(config.config.keys())[0]
        if "save" in form.keys() and form["save"] == "True":
            for key in form:
                if key != "save":
                    config.config[dict_name][key] = form[key]
            config.save()
            load_config(source=dict_name)
            return TEMPLATES.TemplateResponse(
                "config.html",
                {
                    "request": request,
                    "dicts": config.config,
                    "dict_name": dict_name,
                    "comments": COMMENTS,
                    "saved": True,
                    "description": DESCRIPTIONS[dict_name],
                },
            )
        else:
            return TEMPLATES.TemplateResponse(
                "config.html",
                {
                    "request": request,
                    "dicts": config.config,
                    "dict_name": dict_name,
                    "comments": COMMENTS,
                    "description": DESCRIPTIONS[dict_name],
                },
            )

    @app.post("/prefix")
    @app.post("/prefix/{prefix_name}")
    @app.get("/prefix")
    @app.get("/prefix/{prefix_name}")
    async def show_edit_prefix(request: Request, prefix_name: str = ""):
        if not ABLE:
            return "已关闭webui,禁止访问"
        form = await request.form()
        if "change_key" in form.keys() and form["change_key"] == "True":
            new_name = form["new_key"]
            try:
                prefixes.rename(old_name=prefix_name, new_name=new_name)
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prefix.html",
                {
                    "request": request,
                    "prefixes": prefixes.prefixes,
                    "prefix_name": prefix_name,
                    "saved": True,
                },
            )
        elif "save" in form.keys() and form["save"] == "True":
            new_prefix = form["prefix_value"]
            try:
                prefixes.change(prefix_name=prefix_name, prefix=new_prefix)
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prefix.html",
                {
                    "request": request,
                    "prefixes": prefixes.prefixes,
                    "prefix_name": prefix_name,
                },
            )
        elif "delete_key" in form.keys() and form["delete_key"] == "True":
            try:
                prefixes.delete(prefix_name=prefix_name)
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prefix.html",
                {
                    "request": request,
                    "prefixes": prefixes.prefixes,
                    "prefix_name": prefix_name,
                },
            )

        elif "add_key" in form.keys() and form["add_key"] == "True":
            new_key = form["new_key"]
            try:
                prefixes.add(prefix_name=new_key, prefix="请在这里输入要设置的预设内容")
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prefix.html",
                {
                    "request": request,
                    "prefixes": prefixes.prefixes,
                    "prefix_name": prefix_name,
                },
            )
        else:
            return TEMPLATES.TemplateResponse(
                "prefix.html",
                {
                    "request": request,
                    "prefixes": prefixes.prefixes,
                    "prefix_name": prefix_name,
                },
            )

    @app.post("/prompt")
    @app.post("/prompt/{prompt_name}")
    @app.get("/prompt")
    @app.get("/prompt/{prompt_name}")
    async def show_edit_prompt(request: Request, prompt_name: str = ""):
        if not ABLE:
            return "已关闭webui,禁止访问"
        form = await request.form()
        if "change_key" in form.keys() and form["change_key"] == "True":
            new_name = form["new_key"]
            try:
                prompts.rename(old_name=prompt_name, new_name=new_name)
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prompt.html",
                {
                    "request": request,
                    "prompts": prompts.prompts,
                    "prompt_name": prompt_name,
                    "saved": True,
                },
            )
        elif "save" in form.keys() and form["save"] == "True":
            new_prompt = form["prompt_value"]
            try:
                prompts.change(prompt_name=prompt_name, prompt=new_prompt)
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prompt.html",
                {
                    "request": request,
                    "prompts": prompts.prompts,
                    "prompt_name": prompt_name,
                },
            )
        elif "delete_key" in form.keys() and form["delete_key"] == "True":
            try:
                prompts.delete(prompt_name=prompt_name)
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prompt.html",
                {
                    "request": request,
                    "prompts": prompts.prompts,
                    "prompt_name": prompt_name,
                },
            )

        elif "add_key" in form.keys() and form["add_key"] == "True":
            new_key = form["new_key"]
            try:
                prompts.add(prompt_name=new_key, prompt="请在这里输入要设置的预设内容")
            except:
                pass
            return TEMPLATES.TemplateResponse(
                "prompt.html",
                {
                    "request": request,
                    "prompts": prompts.prompts,
                    "prompt_name": prompt_name,
                },
            )
        else:
            return TEMPLATES.TemplateResponse(
                "prompt.html",
                {
                    "request": request,
                    "prompts": prompts.prompts,
                    "prompt_name": prompt_name,
                },
            )


async def run_server():
    web_ui_thread = threading.Thread(target=run_unicorn)
    web_ui_thread.daemon = True
    web_ui_thread.start()


async def start_web_ui():
    global ABLE
    ABLE = True


async def stop_web_ui():
    global ABLE
    ABLE = False


def run_unicorn():
    uvicorn.run(app, host=HOST, port=PORT)


asyncio.run(run_server())
