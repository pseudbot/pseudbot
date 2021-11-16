import inspect
import json as j
from os.path import basename
from PIL import Image, ImageDraw
import re
import requests
from textwrap import shorten, wrap
from time import localtime, strftime, time
import typing


def get_iphone_time_s() -> str:
    ltime = localtime()
    hour = re.sub("^0", "  ", strftime("%I", ltime))
    return hour + ":" + strftime("%M", ltime)


def get_timestamp_s() -> str:
    return "🕑" + str(int(time()))


def surl_prefix(screen_name: str):
    return "https://twitter.com/" + screen_name + "/status/"


def jdump(itms, echo: bool = False, extra_tag: str = None):
    tag = "."
    if extra_tag is not None:
        tag = "." + str(extra_tag) + "."

    dfname = str(inspect.stack()[1][3]) + tag + str(int(time())) + ".dump.json"
    print('[INFO]: Writing JSON dump to "{}"'.format(dfname))
    df = open(dfname, mode="w")

    pretty = j.dumps(itms, sort_keys=True, indent=2)
    if echo is True:
        print(pretty)
    df.write(pretty)

    df.close()


def get_tweet_text(tweet):
    if tweet.retweeted is True:
        text = tweet.retweeted_status.full_text
    else:
        text = tweet.full_text

    return text


def log_t_by_sname(tweet):
    print(
        '[@{}]: "{}" ({})'.format(
            tweet.user.screen_name,
            get_tweet_text(tweet),
            surl_prefix(tweet.user.screen_name) + str(tweet.id),
        )
    )


def _text_wrap(text: str, width: int, height: int = None):
    lines = wrap(text, width=width)
    if height is not None:
        if len(lines) > height:
            lines[height - 1] = shorten(
                lines[height - 1] + " " + lines[height],
                width=width,
                placeholder="...",
            )
            lines = lines[:height]

    return lines


def styled_wrap(text: str, wrap: tuple):
    return "\n".join(_text_wrap(text, wrap[0], wrap[1]))


def text_wrap(text: str, width: int, height: int = None):
    return "\n".join(_text_wrap(text, width, height))


def download_tweet_media(tweet: dict):
    if "extended_entities" in tweet:
        try:
            media = tweet["extended_entities"]["media"]
        except KeyError:
            return

        for item in media:
            dl_url = item["media_url_https"]
            r = requests.get(dl_url, stream=True)
            if r.status_code == 200:
                filename = basename(dl_url)
                print('[MEDIA]: Saving media to "{}"'.format(filename))
                with open(filename, mode="wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)


def square_crop(image: Image) -> Image:
    (width, height) = image.size
    if width != height:
        new_image = None
        if width > height:
            return image.crop((0, 0, height, height))
        else:
            return image.crop((0, 0, width, width))
    else:
        return image


def alpha_comp_prep(
    image: Image, size: tuple, offset: tuple = (0, 0), scale: tuple = None
):
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))

    if scale is not None:
        image = image.resize(size=scale, resample=Image.BICUBIC)

    canvas.paste(image, box=offset)
    return canvas


def circle_mask(size: int):
    ci = Image.new("L", (size, size), 0)

    d = ImageDraw.Draw(ci)
    d.ellipse(xy=(0, 0, size, size), fill=255)

    return ci


def circle_pfp(pfp: Image, size: int = None) -> Image:
    pfp = square_crop(pfp)

    if size is not None:
        pfp = pfp.resize((size, size), resample=Image.BICUBIC)

    (width, height) = pfp.size
    pfp.putalpha(circle_mask(width))

    return pfp


def tuple_add(a: tuple, b: tuple) -> tuple:
    return tuple(map(sum, zip(a, b)))
