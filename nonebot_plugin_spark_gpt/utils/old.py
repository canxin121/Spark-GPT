import asyncio
import base64
from io import BytesIO
import os
from pathlib import Path
from typing import Optional, Union
from PIL import Image, ImageDraw, ImageFont

abs_path = os.path.abspath(__file__)
root = os.path.dirname(abs_path)
DATA_ROOT = root
DATA_PATH = DATA_ROOT + "/TXT2IMG"
FONT_PATH = DATA_PATH + "/font"
IMAGE_PATH = DATA_PATH + "/image"
FONT_FILE = FONT_PATH + "/PingFang Medium.ttf"
MI_BACKGROUND_FILE = IMAGE_PATH + "/mi_background.png"

templates = {
    "mi": {
        "font": str(FONT_FILE),
        "text": {
            "color": (125, 101, 89),
        },
        "title": {
            "color": (125, 101, 89),
        },
        "margin": 80,
        "background": {
            "type": "image",
            "image": str(MI_BACKGROUND_FILE),
        },
        "border": {
            "color": (220, 211, 196),
            "width": 2,
            "margin": 30,
        },
    },
    "simple": {
        "font": str(FONT_FILE),
        "text": {
            "color": (0, 0, 0),
        },
        "title": {
            "color": (0, 0, 0),
        },
        "margin": 50,
        "background": {
            "type": "color",
            "color": (255, 255, 255),
        },
    },
}


class Txt2Img:
    """Convert text to image"""

    font_family: str
    title_font_size: int
    text_font_size: int
    title_line_space: int
    text_line_space: int
    text_max_width: int
    fix_width: bool
    text_color: tuple
    title_color: tuple
    bg_color: tuple

    def __init__(self):
        self.raw_text = str()
        self.font_family = str(FONT_FILE)
        self.title_font_size = 45
        self.text_font_size = 30
        self.title_line_space = 30
        self.text_line_space = 15
        self.text_max_width = 1080
        self.fix_width = True
        self.text_color = (0, 0, 0, 255)
        self.title_color = (0, 0, 0, 255)
        self.bg_color = (255, 255, 255, 0)

    def set_font_family(self, font_family: str):
        """设置字体"""
        self.font_family = font_family

    def set_font_size(self, font_size: int, title_font_size: Optional[int] = None):
        """设置字体大小"""
        self.text_font_size = font_size
        self.text_line_space = font_size // 2
        if title_font_size is not None:
            self.title_font_size = title_font_size
        else:
            self.title_font_size = int(font_size * 1.5)
        self.title_line_space = font_size

    def set_font_color(self, text_color: tuple, title_color: Optional[tuple] = None):
        """设置字体颜色"""
        self.text_color = text_color
        if title_color is not None:
            self.title_color = title_color
        else:
            self.title_color = text_color

    def set_width(self, width: int):
        """设置图片宽度"""
        self.text_max_width = width
        self.fix_width = True

    async def word_wrap(self, text: str, font: ImageFont.FreeTypeFont) -> str:
        """异步自动换行"""
        temp_len = 0
        result = ""
        for ch in text:
            char_w = font.getsize(ch)[0]
            if ch == "\n":
                result += ch
                temp_len = 0
            elif char_w > 0:
                result += ch
                temp_len += char_w
                if temp_len > self.text_max_width - self.text_font_size:
                    temp_len = 0
                    result += "\n"
            await asyncio.sleep(0)  # 让出控制权，避免阻塞事件循环
        result = result.rstrip()
        return result

    async def draw_img(
        self, title: str, text: str, template: Union[str, dict] = "mi"
    ) -> Image.Image:
        """异步绘制给定模板模板下的图片"""

        if isinstance(template, str):
            try:
                template = templates[template]  # type: ignore
            except KeyError:
                template = templates["mi"]  # type: ignore

        try:
            font_family = template["font"]  # type: ignore
            text_color = template["text"]["color"]  # type: ignore
            title_color = template["title"]["color"]  # type: ignore
            margin = int(template["margin"])  # type: ignore
            background = template["background"]  # type: ignore
        except KeyError:
            raise ValueError("Invalid template")

        if not Path(font_family).exists():
            raise ValueError("Invalid font")

        self.set_font_family(font_family)
        self.set_font_color(text_color, title_color)  # type: ignore
        text_img = await self.draw_text(title, text)
        # text_img.show()
        try:
            if background["type"] == "image":  # type: ignore
                out_img = Image.new(
                    "RGBA",
                    (text_img.width + 2 * margin, text_img.height + 2 * margin),
                    (0, 0, 0, 0),
                )
                bg_img = await asyncio.to_thread(Image.open, background["image"])  # type: ignore
                out_img = await tile_image(bg_img, out_img)
            elif background["type"] == "color":  # type: ignore
                out_img = Image.new(
                    "RGBA",
                    (text_img.width + 2 * margin, text_img.height + 2 * margin),
                    background["color"],
                )  # type: ignore
            else:
                raise ValueError("Invalid background type")
        except Exception:
            raise ValueError("Invalid template")

        out_img.paste(text_img, (margin, margin), text_img)
        # out_img.show()
        h = out_img.height
        w = out_img.width
        # out_img.show()
        try:
            border = template["border"]  # type: ignore
            border_color = border["color"]  # type: ignore
            border_width = int(border["width"])  # type: ignore
            border_margin = int(border["margin"])  # type: ignore
            draw = ImageDraw.Draw(out_img)
            draw.rectangle(
                (
                    border_margin,
                    border_margin,
                    out_img.width - border_margin,
                    out_img.height - border_margin,
                ),
                outline=border_color,
                width=border_width,
            )
        except KeyError:
            pass
        except Exception:
            raise ValueError("Invalid template")
        # out_img.show()
        pic = await img2b64(out_img)
        return pic

    async def draw(
        self, title: str, text: str, template: Union[str, dict] = "mi"
    ) -> Union[str, str]:
        """返回一个base64的图片和一个链接"""
        self.raw_text = text
        out_img = await self.draw_img(title, text, template)
        return await img2b64(out_img)

    async def draw_text(self, title: str, text: str) -> Image.Image:
        """输出的只包含标题和正文的文字的背景透明的图片"""
        title_font = ImageFont.truetype(self.font_family, self.title_font_size)
        text_font = ImageFont.truetype(self.font_family, self.text_font_size)

        if title == " ":
            title = ""

        if len(title.split("\n")) > 1:
            title = title.split("\n")[0]

        text = await self.word_wrap(text, text_font)

        lines = text.split("\n")
        text_rows = len(lines)

        title_width = title_font.getsize(title)[0]
        title_height = self.title_font_size + self.title_line_space

        text_height = (
            self.text_font_size * (text_rows + 1)
            + (text_rows + 2) * self.text_line_space
        )

        if title:
            text_total_height = title_height + self.title_line_space + text_height
        else:
            text_total_height = text_height

        out_img = Image.new(
            mode="RGBA",
            size=(self.text_max_width, text_total_height),
            color=self.bg_color,
        )
        draw = ImageDraw.Draw(out_img)

        if title:
            draw.text(
                ((self.text_max_width - title_width) // 2, 0),
                title,
                font=title_font,
                fill=self.text_color,
                spacing=self.title_line_space,
            )
            draw.text(
                (
                    0,
                    title_height + self.title_line_space,
                ),
                text,
                font=text_font,
                fill=self.text_color,
                spacing=self.text_line_space,
            )
        else:
            draw.text(
                (0, 0),
                text,
                font=text_font,
                fill=self.text_color,
                spacing=self.text_line_space,
            )

        return out_img


async def tile_image(small_image: Image.Image, big_image: Image.Image) -> Image.Image:
    """将小图片异步平铺到大图片上"""
    w, h = small_image.size
    queue = asyncio.Queue()

    for i in range(0, big_image.size[0], w):
        for j in range(0, big_image.size[1], h):
            await queue.put((i, j))

    async def paste_worker():
        while not queue.empty():
            i, j = await queue.get()
            big_image.paste(small_image, (i, j))

    workers = [asyncio.create_task(paste_worker()) for _ in range(8)]
    await asyncio.gather(*workers)
    return big_image


async def img2b64(img: Image.Image) -> str:
    """异步图片转 base64"""
    with BytesIO() as buffer:
        await asyncio.to_thread(img.save, buffer, format="PNG")
        base64_str = "base64://" + base64.b64encode(buffer.getvalue()).decode()
        return base64_str


txt2img = Txt2Img()
