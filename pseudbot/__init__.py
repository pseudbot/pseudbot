import typing

from .cli import main as real_main


def main(args: [str], name: str) -> int:
    return real_main(args=args, name=name)
