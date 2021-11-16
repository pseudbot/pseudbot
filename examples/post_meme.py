"""
Test of Discord fake post pixmap generator.
"""
from PIL import Image

from pseudbot.meme.post import Post
from pseudbot.meme.phone_screenshot import PhoneScreenshot
from pseudbot.meme.soyphone import SoyPhone

tt = {
    "channel_name": "staff-feet-pics",
    "posts": [
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "I walk up 4 flights of stairs every single day",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/bonk/E4chSR5WQAQ_Hn3.jpg",
            "text": "it has an orange tip",
            "timestamp": "Today at 5:07 AM",
        },
        {
            "screen_name": "Owen",
            "pfp": "media/phew/EyeJ-4nWEAAFybq.jpg",
            "text": "go look in the fields for it",
            "timestamp": "Today at 5:07 AM",
        },
    ],
}
bt = "Owen #1"

# p = Post(top_text=tt, bottom_text=bt, style="discord")
# pi = p.get_pixmap()
# pi.show()

# This Post() generates an error pixmap
# q = Post(top_text={}, bottom_text=bt, style="discord")
# qi = q.get_pixmap()
# qi.show()

# Makes a fake Discord iPhone screenshot
r = PhoneScreenshot(top_text=tt, bottom_text=bt)
ri = r.get_pixmap()
# ri.show()

# Puts the above screenshot pixmap in an iPhone
s = SoyPhone(screenshot=ri)
si = s.get_pixmap()
si.show()

# Puts an arbitrary pixmap in an iPhone
# i = Image.open("media/phew/EyeJ-4nWEAAFybq.jpg").convert("RGBA")
# t = SoyPhone(screenshot=i)
# ti = t.get_pixmap()
# ti.show()
