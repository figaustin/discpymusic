import discord
import yt_dlp
from typing import Optional

from searchresult import SearchResultVideo


class Song:
    def __init__(self, info, member: discord.Member = None):
        self.info = info
        self.id = info["id"]
        self.title = info["title"]
        self.source = "youtube"
        self.uploader = info["uploader"]
        self.url = info["webpage_url"]
        self.duration = info["duration"]
        self.duration_formatted = info["duration_string"]
        self.is_live = info["is_live"]
        self.views = info["view_count"]
        self.age_limit = info["age_limit"]
        self.likes = info["like_count"]
        self.thumbnail = info["thumbnail"]
        self.member = member
