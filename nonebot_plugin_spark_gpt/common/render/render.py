from os import getcwd
import re
from typing import Union, Literal
from pathlib import Path
import jinja2
import aiofiles
import markdown
import pymdownx
from nonebot.log import logger
from ...poe_pw.pwframework import pwfw

TEMPLATES_PATH = str(Path(__file__).parent / "templates")

env = jinja2.Environment(
    extensions=["jinja2.ext.loopcontrols"],
    loader=jinja2.FileSystemLoader(TEMPLATES_PATH),
    enable_async=True,
)


async def md_to_pic(
    md: str = "",
    md_path: str = "",
    css_path: str = "",
    type: Literal["jpeg", "png"] = "png",
    quality: Union[int, None] = None,
) -> bytes:
    """markdown 转 图片
    Args:
        md (str, optional): markdown 格式文本
        md_path (str, optional): markdown 文件路径
        css_path (str,  optional): css文件路径. Defaults to None.
        type (Literal["jpeg", "png"]): 图片类型, 默认 png
        quality (int, optional): 图片质量 0-100 当为`png`时无效
    Returns:
        bytes: 图片, 可直接发送
    """
    template = env.get_template("markdown.html")
    if not md:
        if md_path:
            md = await read_file(md_path)
        else:
            raise Exception("必须输入 md 或 md_path")
    else:
        md = md.replace("\n","  \n")
    # logger.debug(md)
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

    # logger.debug(md)
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

    if css_path:
        css = await read_file(css_path)
    else:
        css = await read_tpl("github-markdown-light.css") + await read_tpl(
            "pygments-default.css"
        )

    return await html_to_pic(
        template_path=f"file://{css_path if css_path else TEMPLATES_PATH}",
        html=await template.render_async(md=md, css=css, extra=extra),
        type=type,
        quality=quality,
    )


async def html_to_pic(
    html: str,
    wait: int = 0,
    template_path: str = f"file://{getcwd()}",
    type: Literal["jpeg", "png"] = "png",
    quality: Union[int, None] = None,
) -> bytes:
    """html转图片

    Args:
        html (str): html文本
        wait (int, optional): 等待时间. Defaults to 0.
        template_path (str, optional): 模板路径 如 "file:///path/to/template/"
        type (Literal["jpeg", "png"]): 图片类型, 默认 png
        quality (int, optional): 图片质量 0-100 当为`png`时无效
        device_scale_factor: 缩放比例,类型为float,值越大越清晰(真正想让图片清晰更优先请调整此选项)
        **kwargs: 传入 page 的参数

    Returns:
        bytes: 图片, 可直接发送
    """

    # logger.debug(f"html:\n{html}")
    if "file:" not in template_path:
        raise Exception("template_path 应该为 file:///path/to/template")
    page = await pwfw.new_page()
    await page.set_viewport_size({"width": 700, "height": 10})
    await page.goto(template_path)
    await page.set_content(html, wait_until="networkidle")
    await page.wait_for_timeout(wait)
    img_raw = await page.screenshot(
        full_page=True,
        type=type,
        quality=quality,
    )
    await page.close()
    return img_raw


async def read_file(path: str) -> str:
    async with aiofiles.open(path, mode="r") as f:
        return await f.read()


async def read_tpl(path: str) -> str:
    return await read_file(f"{TEMPLATES_PATH}/{path}")
