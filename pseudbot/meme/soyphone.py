from .abc import Meme
from PIL import Image
import typing
from pseudbot.util import alpha_comp_prep


class SoyPhone(Meme):
    def __init__(
        self,
        screenshot: Image = None,
    ):
        self.screenshot = screenshot

        if self.screenshot is None:
            self.error = True
            self.reason = 'No "screenshot" provided for iPhone!'

    def mk_pixmap(self):
        with Image.open("templates/soyphone/soyphone-13.png").convert(
            "RGBA"
        ) as overlay_img:
            self.image = Image.new("RGBA", overlay_img.size, (0, 0, 0, 255))

            self.screenshot = self.screenshot.resize(
                (378, 804), resample=Image.BICUBIC
            )
            self.screenshot = self.screenshot.rotate(
                4.8, resample=Image.BICUBIC, expand=True
            )
            self.screenshot = alpha_comp_prep(
                self.screenshot, size=overlay_img.size, offset=(27, 32)
            )

            overlay_img = Image.alpha_composite(self.screenshot, overlay_img)
            self.image = Image.alpha_composite(self.image, overlay_img)
