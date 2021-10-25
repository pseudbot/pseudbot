import argparse
import inspect
import json as j
import random
from sys import stderr
from time import sleep, time
import tweepy as t
from tweepy.errors import Forbidden, TooManyRequests
import typing

from .pastas import PASTAS


def parse_args(args: [str], name: str):
    parser = argparse.ArgumentParser(prog=name)

    parser.add_argument(
        "-i",
        "--reply-to-id",
        type=int,
        default=None,
        help="ID to reply to, "
        + 'has no affect unless "action" manually directs replies.',
    )
    parser.add_argument(
        "-c",
        "--cfg-json",
        type=argparse.FileType("r"),
        default="pseud.json",
        help="JSON file with Twitter secrets",
    )
    parser.add_argument(
        "action",
        type=str,
        default="timeline",
        help="Method to call",
    )

    return parser.parse_args(args=args)


def get_timestamp_s() -> str:
    return "🕑" + str(int(time()))


class PseudBot:
    last_stat = None

    def __init__(
        self, tcfg: dict, custom_welcome: str = None, last_id: int = None
    ):
        tauth = t.OAuthHandler(tcfg["consumer"], tcfg["consumer_secret"])
        tauth.set_access_token(tcfg["tok"], tcfg["tok_secret"])
        self.tapi = t.API(tauth)

        if custom_welcome is not None:
            welcome_tweet = custom_welcome
        else:
            welcome_tweet = "Powered on at " + str(int(time()))

        self.wstatus = self.tapi.update_status(welcome_tweet)
        self.screen_name = self.wstatus.user.screen_name
        self.url_prefix = "https://twitter.com/" + self.screen_name + "/status/"
        self._log_tweet(welcome_tweet, self.wstatus)

        if last_id is None:
            idr = open("last_id", mode="r")
            self.last_id = int(idr.read())
            idr.close()
            sleep(0.5)
        else:
            self.last_id = last_id

    def _log_tweet(self, msg, tstat) -> None:
        print('[TWEET]: "{}" ({})'.format(msg, self.url_prefix + str(tstat.id)))

    def _jdump(self, itms, echo: bool = False):
        dfname = (
            str(inspect.stack()[1][3]) + "." + str(int(time())) + ".dump.json"
        )
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

        self._jdump(jsons, echo=True)

    def _tweet_pasta(self, id_reply_to: int, pasta: [str]):
        """
        In this house we stan recursion.
        """
        _stat = self.last_stat
        try:
            noodle = pasta.pop(0)
            self.last_stat = self.tapi.update_status(
                noodle, in_reply_to_status_id=id_reply_to
            )
            self._log_tweet(noodle, self.last_stat)
        except Forbidden:
            return _stat
        if len(pasta) > 0:
            pasta[0] = "@" + self.last_stat.user.screen_name + " " + pasta[0]
            sleep(2)
            return self._tweet_pasta(self.last_stat.id, pasta)
        else:
            return self.last_stat

    def hello(self):
        hello_msg = get_timestamp_s() + ": Hello pseudbot"
        hello_stat = self.tapi.update_status(hello_msg)
        self._jdump(hello_stat._json)
        self._log_tweet(hello_msg, hello_stat)

    def write_last_id(self):
        idw = open("last_id", mode="w")
        idw.write(str(self.last_id))
        idw.close()

    def dump_all_mentions(self):
        self.dump_mentions(start_id=1)

    def dump_mentions(self, start_id: int = None):
        if start_id is None:
            start_id = self.last_id

        tweets_j = []
        for tweet in t.Cursor(
            self.tapi.mentions_timeline, since_id=start_id
        ).items():
            if tweet.user.screen_name == self.screen_name:
                continue

            print(
                "Mentioned by @{} in: {}".format(
                    tweet.user.screen_name, self.url_prefix + str(tweet.id)
                )
            )
            tweets_j.append(tweet._json)

            self.last_id = max(tweet.id, self.last_id)
            sleep(2)

        self._jdump(tweets_j)

    def pasta_tweet(self):
        pasta = []
        while len(pasta) < 1:
            pasta = random.choice(PASTAS)

        print("[INFO]: Replying to {}...".format(self.last_id))
        tweets = self.tapi.lookup_statuses([self.last_id])
        for tweet in tweets:
            self._send_pasta_chain(tweet)

    def _send_pasta_chain(self, tweet):
        pasta = []
        while len(pasta) < 1:
            pasta = random.choice(PASTAS)

        if tweet.in_reply_to_screen_name is not None:
            if tweet.in_reply_to_screen_name != self.screen_name:
                parent_name = tweet.in_reply_to_screen_name
            else:
                parent_name = None
                print(
                    "[INFO]: Replying to {}'s mention ".format(
                        tweet.user.screen_name
                    )
                    + "instead of replying to myself..."
                )
        else:
            parent_name = None

        if tweet.in_reply_to_status_id is not None and parent_name is not None:
            pasta[0] = "@" + tweet.in_reply_to_screen_name + " " + pasta[0]
            self.last_stat = self._tweet_pasta(
                tweet.in_reply_to_status_id, pasta
            )
        else:
            pasta[0] = "@" + tweet.user.screen_name + " " + pasta[0]
            self.last_stat = self._tweet_pasta(tweet.id, pasta)

    def reply_mentions(self):
        for tweet in t.Cursor(
            self.tapi.mentions_timeline, since_id=self.last_id
        ).items():
            if tweet.user.screen_name == self.screen_name:
                continue

            self.last_id = max(tweet.id, self.last_id)

            self._send_pasta_chain(tweet)

            if self.last_stat is not None:
                print("Finished chain with {}".format(self.last_stat.id))
            sleep(10)

        self.write_last_id()

    def run_bot(self):
        try:
            while True:
                try:
                    self.reply_mentions()
                    sleep(120)
                except TooManyRequests:
                    cooldown = 1000
                    print(
                        "[WARN]: Rate limited, cooling down for {} seconds...".format(
                            cooldown
                        )
                    )
                    sleep(cooldown)
        except KeyboardInterrupt:
            print()
            shutdown_msg = (
                "Shut down for maintenance at " + str(int(time())) + " 👋"
            )
            self._log_tweet(shutdown_msg, self.tapi.update_status(shutdown_msg))


def callm(pb: PseudBot, methname: str):
    return getattr(pb, methname)()


def main(args: [str], name: str) -> int:
    opts = parse_args(args=args, name=name)

    if opts.action == "run_bot":
        pb = PseudBot(j.loads(opts.cfg_json.read()))
    elif opts.action in ("pasta_tweet"):
        if opts.reply_to_id is not None:
            pb = PseudBot(
                j.loads(opts.cfg_json.read()),
                custom_welcome=get_timestamp_s()
                + ': Running method: "{}"'.format(opts.action),
                last_id=opts.reply_to_id,
            )
        else:
            print("[ERROR]:  Must specify tweet ID to reply to!", file=stderr)
            exit(1)
    else:
        pb = PseudBot(
            j.loads(opts.cfg_json.read()),
            custom_welcome=get_timestamp_s()
            + ': Running method: "{}"'.format(opts.action),
        )
    callm(pb, opts.action)
