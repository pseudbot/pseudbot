from filetype import guess
from os import listdir
import os.path as op


def validate_img_size(media_path: str) -> bool:
    img_sz = op.getsize(media_path)

    if img_sz > 0 and img_sz <= 5242880:
        return True
    else:
        return False


def validate_vid_size(media_path: str) -> bool:
    vid_sz = op.getsize(media_path)

    if vid_sz > 0 and vid_sz <= 1073741824:
        return True
    else:
        return False


def validate_media(media_path: str) -> bool:
    kind = guess(media_path)
    if kind is None:
        return False

    if kind.extension in ("jpg", "jpeg") and kind.mime == "image/jpeg":
        return validate_img_size(media_path)
    elif kind.extension == "png" and kind.mime == "image/png":
        return validate_img_size(media_path)
    if kind.extension == "gif" and kind.mime == "image/gif":
        return validate_img_size(media_path)
    elif kind.extension == "mp4" and kind.mime == "video/mp4":
        return validate_vid_size(media_path)
    elif kind.extension == "mov" and kind.mime == "video/quicktime":
        return validate_vid_size(media_path)
    else:
        return False


def get_media() -> dict:
    media = {}

    media_prefix = op.abspath("media")
    for cat in listdir("media"):
        fullcat = op.join(media_prefix, cat)

        if op.isdir(fullcat):
            items = []
            for itm in listdir(fullcat):
                fullitm = op.join(fullcat, itm)

                if op.isfile(fullitm):
                    if validate_media(fullitm) is True:
                        items.append(fullitm)

            if len(items) > 0:
                media[cat] = items

    return media


MEDIA = get_media()
