from .abc import Meme
from PIL import Image, ImageDraw, ImageFont
import typing

from pseudbot.util import (
    _text_wrap,
    alpha_comp_prep,
    circle_pfp,
    styled_wrap,
    text_wrap,
    tuple_add,
)


class Post(Meme):
    from .post_styles import styles

    def __init__(
        self,
        top_text: dict = None,
        bottom_text: str = None,
        style: str = "discord",
    ):
        self.top_text = top_text
        self.bottom_text = bottom_text
        self.style = style

        self.style_methods = {"discord": self.draw_discord_post}

        self.init_style_posts()

    def get_post_dimens(self) -> int:
        max_dimens = (0, 0)
        offsets_add = {}
        post_items = dict(
            sorted(
                self.styles[self.style]["fields"].items(),
                key=lambda s: s[1]["offset"][1],
            )
        )
        while len(post_items) > 0:
            items = [k for k in post_items.keys()]
            for k in items:
                offset_add = (0, 0)
                if "offset_add" in post_items[k]:
                    if k in offsets_add:
                        offset_add = offsets_add[k]
                    else:
                        continue
                if k not in self.post:
                    if "default" in post_items[k]:
                        self.post[k] = post_items[k]["default"]
                    else:
                        self.post[k] = "default text"

                wrap = post_items[k]["wrap"]
                lines = _text_wrap(self.post[k], wrap[0], wrap[1])
                font = ImageFont.truetype(
                    self.fonts[post_items[k]["font"]], post_items[k]["size"]
                )
                size = font.getsize("\n".join(lines))
                if len(lines) > 1:
                    size = (size[0], size[1] * len(lines))

                offset = tuple_add(post_items[k]["offset"], offset_add)
                _max_dimens = tuple_add(offset, size)

                max_dimens = (
                    max(_max_dimens[0], max_dimens[0]),
                    max(_max_dimens[1], max_dimens[1]),
                )

                if "offset_for" in post_items[k]:
                    for dependent in post_items[k]["offset_for"]:
                        add_x = 0
                        add_y = 0
                        if "x" in post_items[k]["offset_for"][dependent]:
                            add_x = _max_dimens[0]
                        if "y" in post_items[k]["offset_for"][dependent]:
                            add_y = _max_dimens[1]

                        offsets_add[dependent] = (add_x, add_y)

                self.offsets[k] = offset
                post_items.pop(k)

        max_dimens = tuple_add(max_dimens, self.styles[self.style]["margin"])
        return max_dimens

    def draw_post(self) -> Image:
        pass

    def draw_discord_post(self) -> Image:
        pfp_size = 132

        if self.error is True:
            return self.error_pixmap(self.reason)
        else:
            dimens = self.get_post_dimens()

            post_base = Image.new(
                "RGBA", dimens, self.styles[self.style]["background"]
            )

            # Draw circle profile pic
            with alpha_comp_prep(
                circle_pfp(
                    Image.open(self.post["pfp"]).convert("RGBA"),
                    size=pfp_size,
                ),
                size=post_base.size,
            ) as pfp:
                post_base = Image.alpha_composite(post_base, pfp)

            for field in self.styles[self.style]["fields"].keys():
                post_base = self.draw_styled_text(
                    img=post_base,
                    text=self.post[field],
                    style=self.styles[self.style]["fields"][field],
                    offset=self.offsets[field],
                )

            return post_base

    def mk_pixmap(self):
        self.image = self.style_methods[self.style]()
