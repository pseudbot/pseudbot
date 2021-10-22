import argparse
import inspect
import json as j
import tweepy as t
import typing

from .pastas import PASTAS


def parse_args(args: [str], name: str):
    parser = argparse.ArgumentParser(prog=name)

    parser.add_argument(
        "-a",
        "--action",
        type=str,
        default="timeline",
        help="Method to call",
    )
    parser.add_argument(
        "cfg_json",
        type=argparse.FileType("r"),
        help="JSON file with Twitter secrets",
    )

    return parser.parse_args(args=args)


class PseudBot:
    def __init__(self, tcfg: dict):
        tauth = t.OAuthHandler(tcfg["consumer"], tcfg["consumer_secret"])
        tauth.set_access_token(tcfg["tok"], tcfg["tok_secret"])
        self.tapi = t.API(tauth)

    def jdump(self, itms, echo: bool = False):
        dfname = str(inspect.stack()[1][3]) + ".dump.json"
        df = open(dfname, mode="w")

        pretty = j.dumps(itms, sort_keys=True, indent=2)
        if echo is True:
            print(pretty)
        df.write(pretty)

        df.close()

    def timeline(self):
        home_tl = self.tapi.home_timeline()
        jsons = []
        for tweet in home_tl:
            jsons.append(tweet._json)

        self.jdump(jsons, echo=True)

    def hello(self):
        self.jdump(
            self.tapi.update_status(
                "pseudbot is still under construction..."
            )._json
        )


def callm(pb: PseudBot, methname: str):
    return getattr(pb, methname)()


def main(args: [str], name: str) -> int:
    opts = parse_args(args=args, name=name)

    pb = PseudBot(j.loads(opts.cfg_json.read()))
    callm(pb, opts.action)
