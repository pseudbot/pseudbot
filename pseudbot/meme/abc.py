from abc import ABCMeta, abstractmethod
from PIL import Image, ImageDraw, ImageFont
import typing

from pseudbot.pastas import concat_pasta
from pseudbot.util import styled_wrap, text_wrap


class Meme(metaclass=ABCMeta):
    fonts = {
        "old_console": "font/clacon.ttf",
        "phone_sans": "font/Cantarell-VF.otf",
    }
    styles = {}
    style_methods = {}
    offsets = {}
    error = False
    image = None
    reason = ""
    post = None
    posts = None

    def __init__(
        self,
        top_text: dict = None,
        bottom_text: str = None,
    ):
        self.top_text = top_text
        self.bottom_text = bottom_text

    def init_style_posts(self):
        self.check_posts()
        self.check_style()

    def check_posts(self):
        if not "posts" in self.top_text or len(self.top_text["posts"]) < 1:
            self.error = True
            self.reason = 'No "posts" in top_text!'
        else:
            self.posts = self.top_text["posts"]
            self.post = self.top_text["posts"][0]

            if not "screen_name" in self.post:
                self.post["screen_name"] = "⁉"
            if not "text" in self.post:
                self.post["text"] = concat_pasta()
            if not "timestamp" in self.post:
                self.post["timestamp"] = "Today at time"

    def check_style(self):
        if self.style not in self.styles:
            self.error = True
            self.reason = "Invalid style!"
        elif self.style not in self.style_methods:
            self.error = True
            self.reason = "Style not implemented!"

    @abstractmethod
    def help(self) -> str:
        """
        User-callable help for meme generator.
        """
        pass

    @abstractmethod
    def mk_pixmap(self):
        pass

    def get_styles(self) -> [str]:
        return self.styles

    def help(self) -> str:
        """
        User-callable help for meme generator.
        """
        return "TODO"

    def get_text(self) -> tuple:
        return (self.top_text, self.bottom_text)

    def get_pixmap(self):
        if self.image is None:
            if self.error is True:
                return self.error_pixmap(reason=self.reason)
            else:
                self.mk_pixmap()

        return self.image

    def draw_styled_text(
        self, img: Image, text: str, style: dict, offset: tuple = None
    ) -> Image:
        if offset is None:
            offset = style["offset"]

        if "wrap" in style:
            text = styled_wrap(text, style["wrap"])

        align = style["align"] if "align" in style else "left"

        image = self.draw_text(
            img=img,
            text=text,
            offset=offset,
            size=style["size"],
            fill=style["color"],
            variation=style["style"],
            fontname=style["font"],
            align=align,
        )
        return image

    def draw_text(
        self,
        img: Image,
        text: str,
        offset: tuple,
        size: int,
        fill: tuple,
        variation: str = "Regular",
        fontname: str = "phone_sans",
        align="left",
    ) -> Image:
        font = ImageFont.truetype(self.fonts[fontname], size)
        font.set_variation_by_name(variation)

        d = ImageDraw.Draw(img)
        d.text(xy=offset, text=text, fill=fill, font=font, align=align)

        return img

    def error_pixmap(self, reason: str) -> Image:
        efont = ImageFont.truetype("font/clacon.ttf", 70)

        reason = text_wrap(text=reason, width=16, height=5)

        with Image.open("img/pseud-error.png").convert("RGBA") as base_img:
            text_img = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(text_img)

            d.text((292, 466), reason, font=efont, fill=(0, 0, 0, 255))

            out = Image.alpha_composite(base_img, text_img)

        return out
