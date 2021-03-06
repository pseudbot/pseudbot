import random
from sys import stderr
from textwrap import wrap
from time import sleep, time
import tweepy as t
from tweepy.errors import Forbidden, TooManyRequests
import typing

from .command import Command, mk_commands
from .exceptions import *
from .pastas import PASTAS
from .util import (
    get_timestamp_s,
    jdump,
    get_tweet_text,
    log_t_by_sname,
    surl_prefix,
)


class PseudBot:
    last_stat = None

    def __init__(
        self,
        tcfg: dict,
        custom_welcome: str = None,
        last_id: int = None,
        reply_all: bool = True,
        target_screen_name: str = None,
        proxy_url: str = None,
        quiet: bool = False,
        debug: bool = False,
    ):
        self.debug = debug
        self.reply_all = True
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
            tweet_mode="extended",
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
        home_tl = self.tapi.home_timeline(tweet_mode="extended")
        jsons = []
        for tweet in home_tl:
            jsons.append(tweet._json)

        jdump(jsons, extra_tag=self.screen_name)

    def _tweet_media(
        self, id_reply_to: int, parent_screen_names: str, media: [str] = []
    ):
        _stat = self.last_stat
        if self.debug is True:
            print("[DEBUG]: _tweet_media's media: {}".format(media))
        try:
            self.last_stat = self.tapi.update_status_with_media(
                parent_screen_names,
                in_reply_to_status_id=id_reply_to,
                filename=media.pop(0),
            )
        except Forbidden:
            return _stat

        if len(media) > 0:
            sleep(2)
            parent_screen_names = (
                parent_screen_names
                if parent_screen_names.startswith(
                    "@" + self.last_stat.user.screen_name
                )
                else "@"
                + self.last_stat.user.screen_name
                + " "
                + parent_screen_names
            )
            return self._tweet_media(
                self.last_stat.id, parent_screen_names, media
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
            self.tapi.mentions_timeline,
            since_id=start_id,
            tweet_mode="extended",
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

    def dump_tweet(self, status_id: int = None):
        """
        Dump the JSON data dictionary of a specific tweet.
        If called from the CLI, requires ``-i`` to be set.
        """
        if status_id is None:
            status_id = self.last_id

        tweets = self.tapi.lookup_statuses([status_id], tweet_mode="extended")
        jtweets = []
        for tweet in tweets:
            log_t_by_sname(tweet)
            jtweets.append(tweet._json)

        jdump(jtweets, extra_tag=self.last_id)

    def pasta_tweet(self):
        """
        Insert a copy pasta in a Tweet chain manually under a specific
        tweet ID.  Requires ``-i`` to be set if calling from the CLI.
        """
        tweet = self.tapi.lookup_statuses(
            [self.last_id], tweet_mode="extended"
        )[0]
        parents = self._get_reply_parents(tweet)
        parent_screen_names = " ".join(list(map(lambda p: "@" + p[1], parents)))

        pasta = ""
        while len(pasta) < 1:
            pasta = random.choice(PASTAS)

        noodles = self._make_pasta_chain(parent_screen_names, pasta)
        self._tweet_pasta(self.last_id, noodles)

        print("[INFO]: Inserting pasta under {}...".format(self.last_id))

    def run_cmd_tweet(self):
        """
        Parse a specific tweet for a command and post specified pasta(s).
        Requires ``-i`` to be set if calling from the CLI.
        """

        print("[INFO]: Replying to {}...".format(self.last_id))
        tweets = self.tapi.lookup_statuses(
            [self.last_id], tweet_mode="extended"
        )
        for tweet in tweets:
            self._parse_mention(tweet)

    def get_tweet_parents(self):
        """
        Print the parent tuple list (parent_id, reply_to_screen_name).

        Requires ``-i`` to be set if calling from the CLI.
        """
        print(
            self._get_reply_parents(
                self.tapi.lookup_statuses(
                    [self.last_id], tweet_mode="extended"
                )[0]
            )
        )

    def _get_reply_parents(self, tweet) -> [(int, str)]:
        """
        Builds and returns the parent tuple list from a starting tweet:
            (parent_id, reply_to_screen_name)
        """
        if tweet.in_reply_to_screen_name is not None:
            if tweet.in_reply_to_screen_name != self.screen_name:
                parent_name = tweet.in_reply_to_screen_name
            else:
                parent_name = None
                print(
                    "[INFO]: Replying to {}'s mention directly...".format(
                        tweet.user.screen_name
                    )
                )
        else:
            parent_name = None

        parents = []
        if tweet.in_reply_to_status_id is not None and parent_name is not None:
            reply_to_screen_name = tweet.in_reply_to_screen_name
            parent_id = tweet.in_reply_to_status_id
            parents = parents + self._get_reply_parents(
                tweet=self.tapi.lookup_statuses(
                    [tweet.in_reply_to_status_id], tweet_mode="extended"
                )[0]
            )
        else:
            reply_to_screen_name = tweet.user.screen_name
            parent_id = tweet.id

        parents = [(parent_id, reply_to_screen_name)] + parents

        return parents

    def test_parser(self):
        """
        Run the command parser in a dry run (e.g. without sending any tweets) on
        a specific tweet.

        Requires ``-i`` to be set if calling from the CLI.
        """
        self._parse_mention(
            self.tapi.lookup_statuses([self.last_id], tweet_mode="extended")[0],
            wet_run=False,
        )

    def _parse_mention(self, tweet, wet_run: bool = True):
        """
        Parse commands in tweet and do something
        """
        # Each parent in the list is a (parent_id, parent_screen_name) tuple.
        parents = self._get_reply_parents(tweet)
        parent_screen_names = " ".join(list(map(lambda p: "@" + p[1], parents)))

        drybug = False if wet_run is True else True
        if self.debug is True:
            jdump(tweet._json, extra_tag="{}.debug".format(tweet.id))
            drybug = True

        commands = mk_commands(get_tweet_text(tweet), debug=drybug)
        for ci in range(len(commands)):
            command = commands[ci]
            pasta = []
            if len(command.pasta) > 0:
                pasta = self._make_pasta_chain(
                    parent_screen_names, command.pasta
                )
                if wet_run is True:
                    self._tweet_pasta(parents[0][0], pasta, command.media)
                else:
                    print("[DRY]: pasta: {}".format(pasta))
                    print("[DRY]: Such wow, very tweet!")
            elif len(command.media) > 0:
                if wet_run is True:
                    media = command.media
                    self._tweet_media(parents[0][0], parent_screen_names, media)
                else:
                    # TODO: show media in dry mode?
                    print("[DRY]: Such wow, very media!")
            else:
                print(
                    '[WARN]: Unable to parse tweet segment: "{}"'.format(
                        command.text
                    ),
                    file=stderr,
                )
                if self.debug is True:
                    print(
                        "[DEBUG]: error parsing text from "
                        + "commands[{}].  ".format(ci)
                        + "text: {}".format(
                            list(map(lambda c: c.text, commands))
                        )
                    )
                self.dump_tweet(status_id=tweet.id)

    def _make_pasta_chain(self, parent_screen_names: str, in_txt: str) -> [str]:
        """
        Make a text reply chain.
        """
        pasta = []

        in_pasta = wrap(parent_screen_names + " " + in_txt, width=280)
        pasta.append(in_pasta.pop(0))
        while len(in_pasta) > 0:
            tmp_pasta = wrap(
                "@"
                + self.screen_name
                + " "
                + parent_screen_names
                + " "
                + in_pasta.pop(0),
                width=280,
            )
            pasta.append(tmp_pasta.pop(0))
            if len(in_pasta) > 1:
                in_pasta = [" ".join(tmp_pasta) + in_pasta[0]] + in_pasta[1:]
            else:
                try:
                    in_pasta = [" ".join(tmp_pasta) + in_pasta[0]]
                except IndexError:
                    if self.debug is True:
                        print("[DEBUG]: in_pasta empty!")

        return pasta

    def _reply_mentions(self):
        """
        Check mentions since ``last_id`` and reply in each thread with a
        copypasta chain.
        """
        for tweet in t.Cursor(
            self.tapi.mentions_timeline,
            since_id=self.last_id,
            tweet_mode="extended",
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
                "Shut down for maintenance at " + str(int(time())) + " ????"
            )
            self._log_tweet(shutdown_msg, self.tapi.update_status(shutdown_msg))
