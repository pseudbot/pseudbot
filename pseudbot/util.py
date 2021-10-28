import inspect
import json as j
from time import time
import typing


def get_timestamp_s() -> str:
    return "🕑" + str(int(time()))


def surl_prefix(screen_name: str):
    return "https://twitter.com/" + screen_name + "/status/"


def jdump(itms, echo: bool = False):
    dfname = str(inspect.stack()[1][3]) + "." + str(int(time())) + ".dump.json"
    df = open(dfname, mode="w")

    pretty = j.dumps(itms, sort_keys=True, indent=2)
    if echo is True:
        print(pretty)
    df.write(pretty)

    df.close()


def log_t_by_sname(tweet):
    print(
        '[@{}]: "{}" ({})'.format(
            tweet.user.screen_name,
            tweet.text,
            surl_prefix(tweet.user.screen_name) + str(tweet.id),
        )
    )
