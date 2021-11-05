import inspect
import json as j
from os.path import basename
import requests
from time import time
import typing


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
