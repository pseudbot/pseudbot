import argparse
import inspect
import json as j
import random
from time import sleep, time
import tweepy as t
from tweepy.errors import Forbidden, TooManyRequests
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
    last_stat = None

    def __init__(self, tcfg: dict):
        tauth = t.OAuthHandler(tcfg["consumer"], tcfg["consumer_secret"])
        tauth.set_access_token(tcfg["tok"], tcfg["tok_secret"])
        self.tapi = t.API(tauth)

        welcome_tweet = "Testing at " + str(time())
        self.wstatus = self.tapi.update_status(welcome_tweet)
        self.screen_name = self.wstatus.user.screen_name

        idr = open("last_id", mode="r")
        self.last_id = int(idr.read())
        idr.close()
        sleep(0.5)

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

    def tweet_pasta(self, id_reply_to: int, pasta: [str]):
        """
        In this house we stan recursion.
        """
        _stat = self.last_stat
        try:
            self.last_stat = self.tapi.update_status(
                pasta.pop(0), in_reply_to_status_id=id_reply_to
            )
        except Forbidden:
            return _stat
        # print(status)
        if len(pasta) > 0:
            pasta[0] = "@" + self.last_stat.user.screen_name + " " + pasta[0]
            sleep(2)
            return self.tweet_pasta(self.last_stat.id, pasta)
        else:
            return self.last_stat

    def hello(self):
        self.jdump(
            self.tapi.update_status(
                str(time()) + ": pseudbot is still under construction..."
            )._json
        )

    def reply_test(self):
        pasta = random.choice(PASTAS)
        pasta[0] = "@bustin4201 " + pasta[0]
        print(self.tweet_pasta(1451688288591417348, pasta))

    def write_last_id(self):
        idw = open("last_id", mode="w")
        idw.write(str(self.last_id))
        idw.close()

    def reply_mentions(self):
        for tweet in t.Cursor(
            self.tapi.mentions_timeline, since_id=self.last_id
        ).items():
            if tweet.user.screen_name == self.screen_name:
                continue

            # self.jdump(tweet._json)
            # print("Mentioned in: " + str(tweet.id))
            # continue

            self.last_id = max(tweet.id, self.last_id)

            pasta = []
            while len(pasta) < 1:
                pasta = random.choice(PASTAS)

            if tweet.in_reply_to_status_id is not None:
                pasta[0] = "@" + tweet.in_reply_to_screen_name + " " + pasta[0]
                self.last_stat = self.tweet_pasta(tweet.in_reply_to_status_id, pasta)
            else:
                pasta[0] = "@" + tweet.user.screen_name + " " + pasta[0]
                self.last_stat = self.tweet_pasta(tweet.id, pasta)

            if self.last_stat is not None:
                print("Finished chain with {}".format(self.last_stat.id))
            sleep(10)

        self.write_last_id()

    def run_bot(self):
        while True:
            try:
                self.reply_mentions()
                sleep(120)
            except TooManyRequests:
                cooldown = 1000
                print("[WARN]: Rate limited, cooling down for {} seconds...".format(cooldown))
                sleep(cooldown)


def callm(pb: PseudBot, methname: str):
    return getattr(pb, methname)()


def main(args: [str], name: str) -> int:
    opts = parse_args(args=args, name=name)

    pb = PseudBot(j.loads(opts.cfg_json.read()))
    callm(pb, opts.action)
