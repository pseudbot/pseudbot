import random
import re

from .media import MEDIA


class Command:
    pasta = True
    media = []

    def __init__(self, text: str, debug: bool = False):
        self.text = text
        self.debug = debug
        self.parse()

    def parse(self):
        words = re.split(r'[\s.;():"]+', self.text)
        if len(words[-1]) < 1:
            words.pop()

        if self.debug is True:
            print(words)

        stupid_emoji = "🖼" + b"\xef\xb8\x8f".decode()
        if stupid_emoji in words or "🖼" in words:
            for i in range(len(words)):
                if words[i] in ("🖼", stupid_emoji):
                    try:
                        media_category = words[i + 1]
                        i += 1
                    except IndexError:
                        self.pasta = False
                        break

                    if media_category in MEDIA:
                        self.media.append(random.choice(MEDIA[media_category]))

            if len(self.media) == 0:
                self.pasta = True


def mk_commands(text: str) -> [Command]:
    commands = []

    for command_string in text.split("|"):
        commands.append(Command(text=command_string))

    return commands
