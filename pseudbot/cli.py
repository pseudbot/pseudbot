import argparse
import json as j
from sys import stderr
import typing

from .tweet_bot import PseudBot
from .util import get_timestamp_s


def parse_args(args: [str], name: str):
    parser = argparse.ArgumentParser(prog=name)

    parser.add_argument(
        "-i",
        "--reply-to-id",
        type=int,
        default=None,
        help="ID to reply to.  "
        + 'Has no affect unless "action" is meant to be directed at a specific '
        + "ID.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Run Pseudbot in debug mode.",
    )
    parser.add_argument(
        "-s",
        "--screen-name",
        type=str,
        default=None,
        help="User screen name to run action on.  "
        + 'Has no affect unless "action" is meant to be directed at a '
        + "specific user's screen name",
    )
    parser.add_argument(
        "-c",
        "--cfg-json",
        type=argparse.FileType("r"),
        default="pseud.json",
        help="JSON file with Twitter secrets",
    )
    parser.add_argument(
        "-p",
        "--proxy-url",
        type=str,
        default=None,
        help="Use Twitter API through a SOCKS proxy.",
    )
    parser.add_argument(
        "action",
        type=str,
        default="timeline",
        help="Method to call.  "
        + "Use list_actions to see more information about which actions "
        + "are available.",
    )

    return parser.parse_args(args=args)


def callm(pb: PseudBot, methname: str):
    return getattr(pb, methname)()


def main(args: [str], name: str) -> int:
    opts = parse_args(args=args, name=name)
    custom_welcome = get_timestamp_s() + ': Running method: "{}"'.format(
        opts.action
    )
    tcfg = j.loads(opts.cfg_json.read())["twitter"]

    if opts.action == "run_bot":
        pb = PseudBot(
            tcfg=tcfg,
            last_id=opts.reply_to_id,
            proxy_url=opts.proxy_url,
            debug=opts.debug,
        )
    elif opts.action == "list_actions":
        pb = PseudBot(tcfg=tcfg, quiet=True, debug=opts.debug)
    elif opts.action in (
        "pasta_tweet",
        "dump_tweet",
        "run_cmd_tweet",
        "get_tweet_parents",
        "test_parser",
    ):
        if opts.reply_to_id is not None:
            pb = PseudBot(
                tcfg=tcfg,
                custom_welcome=custom_welcome,
                last_id=opts.reply_to_id,
                proxy_url=opts.proxy_url,
                debug=opts.debug,
            )
        else:
            print(
                "[ERROR]:  Must specify tweet ID with -i",
                file=stderr,
            )
            exit(1)
    elif opts.action in ("user_timeline",):
        print(opts.action)
        if opts.screen_name is not None:
            pb = PseudBot(
                tcfg=tcfg,
                custom_welcome=custom_welcome,
                last_id=opts.reply_to_id,
                target_screen_name=opts.screen_name,
                proxy_url=opts.proxy_url,
                debug=opts.debug,
            )
        else:
            print(
                "[ERROR]:  Must specify screen name with -s",
                file=stderr,
            )
            exit(1)
    else:
        pb = PseudBot(
            tcfg=tcfg,
            custom_welcome=custom_welcome,
            last_id=opts.reply_to_id,
            proxy_url=opts.proxy_url,
            debug=opts.debug,
        )
    callm(pb, opts.action)
