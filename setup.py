from setuptools import setup

try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

# install_requires sucks, I don't know why and I really
# don't care, so I do this:
pipmain(["install", "-r", "requirements.txt"])

scripts = ["scripts/pseudbot", "scripts/fetch-media"]

setup(
    name="pseudbot",
    version="0.1",
    author="Andrew Rogers",
    description="Rick and Morty copypasta bot",
    author_email="tuxlovesyou@gmail.com",
    packages=["pseudbot", "pseudbot.meme"],
    include_package_data=True,
    scripts=scripts,
)
