styles = {
    "discord": {
        "margin": (0, 43),
        "fields": {
            "screen_name": {
                "font": "phone_sans",
                "style": "Extra Bold",
                "offset": (169, 0),
                "size": 59,
                "color": (255, 255, 255, 255),
                "default": "XxX_HungDaddy_XxX_69",
                "offset_for": {
                    "timestamp": "x",
                    "text": "y",
                },
                "wrap": (30, 1),
            },
            "text": {
                "font": "phone_sans",
                "style": "Regular",
                "offset": (169, 2),
                "offset_add": True,
                "size": 59,
                "color": (255, 255, 255, 255),
                "wrap": (40, 20),
            },
            "timestamp": {
                "font": "phone_sans",
                "style": "Regular",
                "offset": (66, 17),
                "offset_add": True,
                "size": 35,
                "color": (112, 115, 122, 255),
                "default": "Today at 5:07 AM",
                "wrap": (30, 1),
            },
        },
        "background": (54, 57, 64, 255),
        "bars": [
            {
                "top": True,
                "bg_img": "templates/discord-phone/discord-heading-notxt-no-notification-notime.png",
                "alt_bg_img": "templates/discord-phone/discord-heading-notxt.png",
                "offset": (0, 0),
                "text": {
                    "font": "phone_sans",
                    "style": "Bold",
                    "offset": (286, 174),
                    "size": 58,
                    "color": (255, 255, 255, 255),
                    "content": "channel_name",
                    "default": "chat",
                },
            },
            {
                "bottom": True,
                "bg_img": "templates/discord-phone/discord-iphone-bottom-bar.png",
                "offset": (0, 2080),
                "text": {
                    "font": "phone_sans",
                    "style": "Regular",
                    "offset": (380, 62),
                    "size": 49,
                    "color": (112, 115, 122, 255),
                    "format": "Message #%%%",
                    "content": "channel_name",
                    "default": "Message #chat",
                },
            },
        ],
    },
    "twitter": {},
}

time_style = {
    "size": 54,
    "offset": (48, 38),
    "font": "phone_sans",
    "style": "Bold",
    "fill": {"discord": (255, 255, 255, 255)},
}
