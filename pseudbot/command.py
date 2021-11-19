import random
import re

from .media import MEDIA
from .pastas import PASTAS


class Command:
    pasta = ""
    media = []
    target = None

    error = None
    reason = None

    def __init__(self, text: str, debug: bool = False):
        self.text = re.sub(r"[\ufe0f]", "", text, re.UNICODE)
        self.debug = debug
        self.parse()

    def parse(self):
        words = re.split(r'[\s.;():"]+', self.text)
        if len(words[-1]) < 1:
            words.pop()

        if self.debug is True:
            print('[DEBUG]: words: "{}"'.format(words))

        lexed = {
            "all": [],
            "media": [],
            "url_media": [],
            "soyphone": [],
        }

        do_pasta = True
        for i in range(len(words)):
            if words[i] == "🖼":
                lexed["media"].append(i)
                lexed["all"].append(i)

                media_category = ""
                try:
                    media_category = words[i + 1]
                    i += 1
                except IndexError:
                    do_pasta = False
                    break

                if media_category in MEDIA:
                    self.media.append(random.choice(MEDIA[media_category]))
                else:
                    self.error = True
                    self.reason = 'Could not find media category: "{}"'.format(
                        media_category
                    )
            if words[i] == "😲🤳":
                lexed["soyphone"].append(i)
                lexed["all"].append(i)

        if len(self.media) == 0 and len(self.text) == 0:
            do_pasta = True

        if self.debug is True:
            print("[DEBUG]: do_pasta: {}".format(do_pasta))

        if do_pasta is True:
            self.pick_pasta()

    def pick_pasta(self):
        while len(self.pasta) < 1:
            self.pasta = random.choice(PASTAS)


def mk_commands(text: str, debug: bool = False) -> [Command]:
    commands = []

    for command_string in text.split("|"):
        commands.append(Command(text=command_string, debug=debug))

    return commands
