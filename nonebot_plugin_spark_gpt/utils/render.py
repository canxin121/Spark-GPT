from pathlib import Path

import aiofiles
import markdown
from nonebot import require

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import (
    html_to_pic
)

from jinja2 import Environment, FileSystemLoader

TEMPLATES_PATH = Path(__file__).parent / "templates"
env = Environment(extensions=["jinja2.ext.loopcontrols"],
                  loader=FileSystemLoader(str(Path(__file__).parent / "templates")), enable_async=True, )
menu_template = env.get_template('menu.html')
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

    css = await read_tpl("markdown.css") + await read_tpl(
        "pygments-default.css"
    )
    html = await text_template.render_async(md=md, font_path=Font_Path, css=css, extra=extra)
    return await html_to_pic(
        html=html,
        viewport={"width": width, "height": 10},
    )


async def menu_to_pic(menu: dict, width: int, headline: str = "菜单", description: str = "1.1.7",
                      font_size: int = 15) -> bytes:
    html = await menu_template.render_async(headline=headline, menu=menu, description=description,
                                            font_path_texttoimg=Font_Path, font_size=font_size)
    return await html_to_pic(html, viewport={"width": width, "height": 10})
