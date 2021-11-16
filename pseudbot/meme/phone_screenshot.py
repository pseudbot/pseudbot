from .abc import Meme
from PIL import Image, ImageDraw, ImageFont
import typing

from pseudbot.meme.post import Post
from pseudbot.util import (
    alpha_comp_prep,
    circle_pfp,
    get_iphone_time_s,
    text_wrap,
    tuple_add,
)


class PhoneScreenshot(Meme):
    from .post_styles import styles, time_style

    def __init__(
        self,
        top_text: dict = None,
        bottom_text: str = None,
        style: str = "discord",
        width: int = 1200,
        height: int = 2340,
        notification: str = None,
    ):
        self.top_text = top_text
        self.bottom_text = bottom_text
        self.style = style
        self.width = width
        self.height = height
        self.notification = notification

        self.style_methods = {"discord": self.mk_pixmap}

        self.init_style_posts()

        if self.notification is not None:
            self.notification_style = {
                "offset": (102, 91),
                "no_text_img": "templates/iphone/iphone-noti-grindr-text.png",
                "icon": {
                    "offset": (26, 34),
                    "size": (62, 62),
                    "files": {
                        "grindr": "templates/iphone/icons/notification/grindr.png"
                    },
                },
                "text": {
                    "app_name": {
                        "font": "phone_sans",
                        "style": "Regular",
                        "size": 35,
                        "offset": (106, 53),
                    },
                    "heading": {
                        "font": "phone_sans",
                        "style": "Regular",
                        "size": 35,
                        "offset": (34, 128),
                    },
                    "body": {
                        "font": "phone_sans",
                        "style": "Regular",
                        "size": 35,
                        "offset": (34, 181),
                    },
                },
            }

    def overlay_noti(base_img: Image) -> Image:
        return base_img

    def mk_bars(self) -> Image:
        base_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        for bar in self.styles[self.style]["bars"]:
            is_top = False
            is_bottom = False
            do_time = False
            bg_img_path = bar["bg_img"]

            if "top" in bar:
                if bar["top"] is True:
                    is_top = True
                    do_time = True
                    if self.notification is not None:
                        do_time = False
                        if "alt_bg_img" in bar:
                            bg_img_path = self.bar["alt_bg_img"]

            if "bottom" in bar:
                if bar["bottom"] is True:
                    is_bottom = True

            with Image.open(bg_img_path).convert("RGBA") as _bar_img:
                with alpha_comp_prep(
                    Image.open(bg_img_path).convert("RGBA"),
                    size=base_img.size,
                    offset=bar["offset"],
                ) as bar_img:
                    if "text" in bar:
                        try:
                            if bar["text"]["content"] in self.top_text:
                                if "format" in bar["text"]:
                                    bar_text = bar["text"]["format"].replace(
                                        "%%%",
                                        self.top_text[bar["text"]["content"]],
                                    )
                                else:
                                    bar_text = self.top_text[
                                        bar["text"]["content"]
                                    ]
                            else:
                                bar_text = bar["text"]["default"]
                        except KeyError:
                            bar_text = "default text"

                        bar_img = self.draw_text(
                            img=bar_img,
                            text=bar_text,
                            offset=tuple_add(
                                bar["text"]["offset"], bar["offset"]
                            ),
                            size=bar["text"]["size"],
                            fill=bar["text"]["color"],
                            variation=bar["text"]["style"],
                            fontname=bar["text"]["font"],
                        )

                    if do_time is True:
                        bar_img = self.draw_text(
                            img=bar_img,
                            text=get_iphone_time_s(),
                            offset=self.time_style["offset"],
                            size=self.time_style["size"],
                            fill=self.time_style["fill"][self.style],
                            variation=self.time_style["style"],
                            fontname=self.time_style["font"],
                        )

                    base_img = Image.alpha_composite(base_img, bar_img)

                    if is_bottom is True:
                        self.bottom_y_offset = 0 - _bar_img.size[1]

        if self.notification is not None:
            base_img = self.overlay_noti(base_img)

        return base_img

    def arrange_posts(self) -> Image:
        post_base = Image.new(
            "RGBA",
            (self.width, self.height),
            self.styles[self.style]["background"],
        )

        x_offset = 33
        y_offset = self.height

        if hasattr(self, "bottom_y_offset"):
            y_offset = y_offset + self.bottom_y_offset

        for post in reversed(self.posts):
            p = Post(
                top_text={"posts": [post]},
                bottom_text=self.bottom_text,
                style=self.style,
            )
            post_img = p.get_pixmap()
            y_offset = y_offset - post_img.size[1]
            post_base.paste(post_img, box=(x_offset, y_offset))

            if y_offset < 0:
                break

        return post_base

    def mk_pixmap(self):
        bars = self.mk_bars()  # Must be done before making posts!
        posts = self.arrange_posts()

        self.image = Image.alpha_composite(posts, bars)
