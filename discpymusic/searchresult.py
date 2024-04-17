import discord

class SearchResultVideo:
    def __init__(self, info, member: discord.Member) -> None:
        self.id = info["id"]
        self.url = info["link"]
        self.thumbnail = info["thumbnails"][0]["url"]
        self.title = info["title"]
        self.duration = info["duration"]
        self.views = info["viewCount"]["text"]
        self.channel_name = info["channel"]["name"]
        self.member = member
