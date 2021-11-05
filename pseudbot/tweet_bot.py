import random
import re
from sys import stderr
from textwrap import indent
from time import sleep, time
import tweepy as t
from tweepy.errors import Forbidden, TooManyRequests
import typing

from .exceptions import *
from .media import MEDIA
from .pastas import PASTAS
from .util import get_timestamp_s, jdump, log_t_by_sname, surl_prefix


class PseudBot:
    last_stat = None

    def __init__(
        self,
        tcfg: dict,
        custom_welcome: str = None,
        last_id: int = None,
        target_screen_name: str = None,
        proxy_url: str = None,
        quiet: bool = False,
    ):
        tauth = t.OAuthHandler(tcfg["consumer"], tcfg["consumer_secret"])
        tauth.set_access_token(tcfg["tok"], tcfg["tok_secret"])

        if proxy_url is not None:
            self.tapi = t.API(tauth, proxy=proxy_url)
        else:
            self.tapi = t.API(tauth)

        if quiet is False:
            if custom_welcome is not None:
                welcome_tweet = custom_welcome
            else:
                welcome_tweet = "Powered on at " + str(int(time()))

            self.target_screen_name = target_screen_name

            self.wstatus = self.tapi.update_status(welcome_tweet)
            self.screen_name = self.wstatus.user.screen_name
            self.url_prefix = (
                "https://twitter.com/" + self.screen_name + "/status/"
            )
            self._log_tweet(welcome_tweet, self.wstatus)

        if last_id is None:
            idr = open("last_id", mode="r")
            self.last_id = int(idr.read())
            idr.close()
            sleep(0.5)
        else:
            self.last_id = last_id

    def list_actions(self):
        """
        List actions that Pseudbot can run.
        """
        actions = [
            meth_name
            for meth_name in dir(self)
            if callable(getattr(self, meth_name))
            and not meth_name.startswith("_")
        ]
        for action_name in actions:
            print(action_name + ":", end="")
            docstr = getattr(self, action_name).__doc__
            print(docstr)
            if docstr is None:
                print()

    def _log_tweet(self, msg, tstat) -> None:
        print('[TWEET]: "{}" ({})'.format(msg, self.url_prefix + str(tstat.id)))

    def _log_tweet_by_sname(self, tweet):
        print(
            '[@{}]: "{}" ({})'.format(
                tweet.user.screen_name,
                tweet.text,
                surl_prefix(tweet.user.screen_name) + str(tweet.id),
            )
        )

    def _check_sname_exists(self):
        if self.target_screen_name is None:
            raise PseudBotNoTargetScreenName

    def user_timeline(self):
        """
        Get all tweets from a user's timeline.
        Requires ``target_screen_name`` to be set
        (set by ``-s`` if using the CLI).
        """
        self._check_sname_exists()
        tweets_j = []

        rq_n = 0
        for tweet in t.Cursor(
            self.tapi.user_timeline,
            screen_name=self.target_screen_name,
            since_id=1,
        ).items():
            log_t_by_sname(tweet)
            tweets_j.append(tweet._json)
            sleep(0.2)
            rq_n += 1
            if rq_n % 899 == 0:
                print(
                    "[WARN]: At standard v1.1 API limit!  "
                    + "Sleeping for 15 minutes...",
                    file=stderr,
                )
                sleep(901)

        jdump(tweets_j, extra_tag=self.target_screen_name)

    def timeline(self):
        """
        Get and dump recent tweets from your Pseudbot account's home timeline.
        """
        home_tl = self.tapi.home_timeline()
        jsons = []
        for tweet in home_tl:
            jsons.append(tweet._json)

        jdump(jsons, extra_tag=self.screen_name)

    def _tweet_media(
        self, id_reply_to: int, parent_screen_name: str, media: [str] = []
    ):
        _stat = self.last_stat
        try:
            self.last_stat = self.tapi.update_status_with_media(
                "@" + parent_screen_name,
                in_reply_to_status_id=id_reply_to,
                filename=media.pop(0),
            )
        except Forbidden:
            return _stat

        if len(media) > 0:
            sleep(2)
            return self._tweet_media(
                self.last_stat.id, self.last_stat.user.screen_name, media
            )
        else:
            return self.last_stat

    def _tweet_pasta(self, id_reply_to: int, pasta: [str], media: [str] = []):
        """
        Recursively tweet an entire pasta, noodle by noodle::
            In this house we stan recursion.
        """
        _stat = self.last_stat
        try:
            noodle = pasta.pop(0)
            if len(media) > 0:
                self.last_stat = self.tapi.update_status_with_media(
                    noodle,
                    in_reply_to_status_id=id_reply_to,
                    filename=media.pop(0),
                )
            else:
                self.last_stat = self.tapi.update_status(
                    noodle, in_reply_to_status_id=id_reply_to
                )
            self._log_tweet(noodle, self.last_stat)
        except Forbidden:
            return _stat
        if len(pasta) > 0:
            pasta[0] = "@" + self.last_stat.user.screen_name + " " + pasta[0]
            sleep(2)
            return self._tweet_pasta(self.last_stat.id, pasta, media)
        else:
            return self.last_stat

    def hello(self):
        """
        Tweet "Hello pseudbot" with a timestamp.
        """
        hello_msg = get_timestamp_s() + ": Hello pseudbot"
        hello_stat = self.tapi.update_status(hello_msg)
        jdump(hello_stat._json)
        self._log_tweet(hello_msg, hello_stat)

    def _write_last_id(self):
        """
        Write the tweet ID of the last mention responded to.
        """
        idw = open("last_id", mode="w")
        idw.write(str(self.last_id))
        idw.close()

    def dump_all_mentions(self):
        """
        Dump all times your bot has been mentioned.
        """
        self.dump_mentions(start_id=1)

    def dump_mentions(self, start_id: int = None):
        """
        Dump all mentions since ``last_id``.
        Override with ``-i`` on the command line.
        """
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

        jdump(tweets_j)

    def dump_tweet(self):
        """
        Dump the JSON data dictionary of a specific tweet.
        If called from the CLI, requires ``-i`` to be set.
        """
        tweets = self.tapi.lookup_statuses([self.last_id])
        jtweets = []
        for tweet in tweets:
            log_t_by_sname(tweet)
            jtweets.append(tweet._json)

        jdump(jtweets, extra_tag=self.last_id)

    def pasta_tweet(self):
        """
        Insert a copy pasta in a Tweet chain manually starting from a specific
        tweet ID.  Requires ``-i`` to be set if calling from the CLI.
        """
        pasta = []
        while len(pasta) < 1:
            pasta = random.choice(PASTAS)

        print("[INFO]: Replying to {}...".format(self.last_id))
        tweets = self.tapi.lookup_statuses([self.last_id])
        for tweet in tweets:
            self._send_pasta_chain(tweet)

    def _get_reply_parent(self, tweet) -> (int, str):
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
            reply_to_screen_name = tweet.in_reply_to_screen_name
            parent_id = tweet.in_reply_to_status_id
        else:
            reply_to_screen_name = tweet.user.screen_name
            parent_id = tweet.id

        return (parent_id, reply_to_screen_name)

    def _parse_mention(self, tweet):
        """
        Parse commands in tweet and do something
        """
        (parent_id, parent_screen_name) = self._get_reply_parent(tweet)

        for command_string in tweet.text.split("|"):
            words = re.split(r'[\s.;():"]+', command_string)
            media = []
            do_pasta = True

            stupid_emoji = "🖼" + b"\xef\xb8\x8f".decode()
            if stupid_emoji in words or "🖼" in words:
                for i in range(len(words)):
                    if words[i] in ("🖼", stupid_emoji):
                        try:
                            media_category = words[i + 1]
                            i += 1
                        except IndexError:
                            do_pasta = False
                            break

                        if media_category in MEDIA:
                            media.append(random.choice(MEDIA[media_category]))

                if len(media) == 0:
                    do_pasta = True

            if do_pasta is True:
                pasta = self._make_pasta_chain(parent_screen_name)
                self._tweet_pasta(parent_id, pasta, media)
            elif len(media) > 0:
                self._tweet_media(parent_id, parent_screen_name, media)
            else:
                print(
                    '[WARN]: Unable to parse tweet segment: "{}"'.format(
                        command_string
                    ),
                    file=stderr,
                )

    def _make_pasta_chain(self, parent_screen_name: str) -> [str]:
        """
        Send a copypasta chain.
        """
        pasta = []
        while len(pasta) < 1:
            pasta = random.choice(PASTAS)

        pasta[0] = "@" + parent_screen_name + " " + pasta[0]

        return pasta

    def _reply_mentions(self):
        """
        Check mentions since ``last_id`` and reply in each thread with a
        copypasta chain.
        """
        for tweet in t.Cursor(
            self.tapi.mentions_timeline, since_id=self.last_id
        ).items():
            if tweet.user.screen_name == self.screen_name:
                continue

            self.last_id = max(tweet.id, self.last_id)

            self._parse_mention(tweet)

            if self.last_stat is not None:
                print("Finished chain with {}".format(self.last_stat.id))
            sleep(10)

        self._write_last_id()

    def run_bot(self):
        """
        Start Pseudbot in its main mode: mention listener mode.
        """
        try:
            while True:
                try:
                    self._reply_mentions()
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
