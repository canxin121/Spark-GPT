from pathlib import Path
from typing import Optional

import aiofiles
import markdown
from nonebot import require

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import html_to_pic

from jinja2 import Environment, FileSystemLoader

TEMPLATES_PATH = Path(__file__).parent / "templates"
env = Environment(
    extensions=["jinja2.ext.loopcontrols"],
    loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
    enable_async=True,
)
list_template = env.get_template("list.html")
menu_template = env.get_template("menus.html")
text_template = env.get_template("markdown.html")

Font_Path = (TEMPLATES_PATH / "PingFang.ttf").as_uri()


async def read_file(path: str) -> str:
    async with aiofiles.open(path, mode="r") as f:
        return await f.read()


async def read_tpl(path: str) -> str:
    return await read_file(f"{TEMPLATES_PATH}/{path}")


async def md_to_pic(
        md: str,
        width: int = 600,
):
    md = markdown.markdown(
        md,
        extensions=[
            "pymdownx.tasklist",
            "tables",
            "fenced_code",
            "codehilite",
            "mdx_math",
            "pymdownx.tilde",
        ],
        extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
    )

    extra = ""
    if "math/tex" in md:
        katex_css = await read_tpl("katex/katex.min.b64_fonts.css")
        katex_js = await read_tpl("katex/katex.min.js")
        mathtex_js = await read_tpl("katex/mathtex-script-type.min.js")
        extra = (
            f'<style type="text/css">{katex_css}</style>'
            f"<script defer>{katex_js}</script>"
            f"<script defer>{mathtex_js}</script>"
        )

    css = await read_tpl("markdown.css") + await read_tpl("pygments-default.css")
    html = await text_template.render_async(
        md=md, font_path=Font_Path, css=css, extra=extra
    )
    return await html_to_pic(
        html=html,
        viewport={"width": width, "height": 10},
    )


async def list_to_pic(
        _list: dict,
        width: int,
        headline: str = "列表",
        description: str = "1.1.8",
        font_size: int = 15,
) -> bytes:
    """list should be {"func1":"description of func","func2":"description of func2"}"""
    html = await list_template.render_async(
        headline=headline,
        list=_list,
        description=description,
        font_path=Font_Path,
        font_size=font_size,
    )
    return await html_to_pic(html, viewport={"width": width, "height": 10})


async def menu_to_pic(menu: dict, width: int, colors: Optional[dict] = None) -> bytes:
    """
    #菜单格式示例
    menu = {
        "私有bot": {"des": "使用和管理自己独有的bot的命令,私有bot只有主人可使用,其他人无法使用", "funcs": {
            f"{PRIVATE_COMMAND}bot名称+询问的问题": "与指定属于自己的bot对话\n(可使用'回复'某bot最后一个答案来连续和它对话)\n(可回复'清除历史','刷新对话'来清除bot的对话记忆)",
            f"{PRIVATE_COMMAND}所有bot": "查询所有的可用的私有的bot,以获取bot名称和相关信息",
            f"{PRIVATE_COMMAND}创建bot": "创建新的私有的bot",
            f"{PRIVATE_COMMAND}改名bot": "更改自己的bot的名称",
            f"{PRIVATE_COMMAND}删除bot": "删除指定自己的bot",
        }},
        "公有bot": {"des": "使用公有bot的命令", "funcs": {
            f"{PUBLIC_COMMAND}bot名称+询问的问题": "与指定属于公共的bot对话\n(可使用'回复'某bot最后一个答案来连续和它对话)\n(可回复'清除历史','刷新对话'来清除bot的对话记忆)",
            f"{PUBLIC_COMMAND}所有bot": "查询所有的可用的公共的bot,以获取bot名称和相关信息",
        }}
    }
    # 蓝白配色示例
    colors = {
        "html_bg": "#d9d9d9",  # 整体背景颜色
        "menu_header_bg": "#E5F3F9",  # 菜单标题和描述的背景颜色
        "grid_bg": "#ffffff",  # 命令表格背景颜色
        "func_name_pre": "#8D3C1E",  # 命令前的'#'的颜色
        "func_index_text": "#FFFFFF",  # 命令前的索引的数字的颜色
        "func_index_bg": "#8D3C1E",  # 命令前的索引的数字的圆形背景颜色
    }
    """

    if colors is None:
        colors = {
            "html_bg": "#d9d9d9",  # 整体背景颜色
            "menu_header_bg": "#E5F3F9",  # 菜单标题和描述的背景颜色
            "grid_bg": "#ffffff",  # 命令表格背景颜色
            "func_name_pre": "#8D3C1E",  # 命令前的'#'的颜色
            "func_index_text": "#FFFFFF",  # 命令前的索引的数字的颜色
            "func_index_bg": "#8D3C1E",  # 命令前的索引的数字的圆形背景颜色
        }
    html = await menu_template.render_async(
        menus=menu, colors=colors, font_path=Font_Path
    )
    return await html_to_pic(html, viewport={"width": width, "height": 10})
