from pathlib import Path

import imgkit
import markdown
from charset_normalizer import from_bytes
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from mdx_math import MathExtension
from nonebot.utils import run_sync
from pygments.formatters import HtmlFormatter
from pygments.styles.xcode import XcodeStyle

ASSETS_PATH = Path(__file__).parent / "assets"
TEMP_PATH = Path(__file__).parent / "temp.jpeg"
TEMP_PATH.touch()
template_html = ""


@run_sync
def string_to_pic(
        string: str, output_path: str, width: int = 2200, zoom: int = 2, quality: int = 94
):
    return imgkit.from_string(
        string,
        output_path,
        {
            "enable-local-file-access": "",
            "allow": ASSETS_PATH,
            "width": width,
            "enable-javascript": "",
            "zoom": zoom,
            "quality": quality,
            "quiet": "",
        },
        None,
        None,
        None,
        None,
    )


@run_sync
def file_to_pic(
        file_path: str,
        output_path: str,
        width: int = 2200,
        zoom: int = 2,
        quality: int = 94,
):
    return imgkit.from_file(
        file_path,
        output_path,
        output_path,
        {
            "enable-local-file-access": "",
            "allow": ASSETS_PATH,
            "width": width,
            "enable-javascript": "",
            "zoom": zoom,
            "quality": quality,
            "quiet": "",
        },
        None,
        None,
        None,
        None,
    )


@run_sync
def url_to_pic(
        url: str, output_path: str, width: int = 2200, zoom: int = 2, quality: int = 94
):
    return imgkit.from_url(
        url,
        output_path,
        output_path,
        {
            "enable-local-file-access": "",
            "allow": ASSETS_PATH,
            "width": width,
            "enable-javascript": "",
            "zoom": zoom,
            "quality": quality,
            "quiet": "",
        },
        None,
        None,
        None,
        None,
    )


with open(ASSETS_PATH / "template.html", "rb") as f:
    guessed_str = from_bytes(f.read()).best()
    if not guessed_str:
        raise ValueError("无法识别 Markdown 模板 template.html")

    # 获取 Pygments 生成的 CSS 样式
    highlight_css = HtmlFormatter(style=XcodeStyle).get_style_defs(".highlight")

    template_html = str(guessed_str).replace("{highlight_css}", highlight_css)


class DisableHTMLExtension(markdown.Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.deregister("html")
        md.preprocessors.deregister("html_block")


extensions = [
    MathExtension(enable_dollar_delimiter=True),  # 开启美元符号渲染
    CodeHiliteExtension(
        linenums=False, css_class="highlight", noclasses=False, guess_lang=True
    ),  # 添加代码块语法高亮
    TableExtension(),
    "fenced_code",
]
md = markdown.Markdown(extensions=extensions)


@run_sync
def text_to_html(text: str) -> str:
    text = text.replace("\n", "  \n")
    content = md.convert(text)
    css_style = HtmlFormatter(style=XcodeStyle).get_style_defs(".highlight")

    content = f"<style>{css_style}</style>\n{content}"
    html = (
        template_html.replace("{path_texttoimg}", ASSETS_PATH.as_uri())
        .replace("{content}", content)
        .replace("{font_path_texttoimg}", (ASSETS_PATH / "PingFang.ttf").as_uri())
    )
    return html


async def txt_to_pic(
        text: str,
        output_path: Path = TEMP_PATH,
        width: int = 2200,
        zoom: int = 2,
        quality: int = 100,
):
    html = await text_to_html(text)
    if not output_path.exists():
        output_path.touch()
    await string_to_pic(html, str(output_path.absolute()), width, zoom, quality)
    return output_path
