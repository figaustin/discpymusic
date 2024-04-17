import discord
import re
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
from voice import DiscPyMusicVoice
from searchresult import SearchResultVideo
from song import Song
from music_queue import Queue


URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

YTDL_OPTIONS_DEFAULT = {"format": "bestaudio/best", "quiet": "true"}
FFMPEG_OPTIONS_DEFAULT = "-vn"
FFMPEG_BEFORE_OPTIONS_DEFAULT = (
    "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
)


class DiscPyMusic:
    """
    Create an instance of this object to use main functionality of the DiscPyMusic library. 

    Parameters
    ----------
    client: :class:`Client`
        A client obj from the discord.py library. `Bot` can also be used
    ytdl_options: :class:`dict`
        Options for use with YoutubeDL. If you are not sure what to use, leave this as default.
    ffmpeg_options: :class:`dict`
        Extra command line arguments to pass to ffmpeg after the -i flag. If you are not sure what to use, leave this as default.
    ffmpeg_before_options: :class:`dict`
        Extra command line arguments to pass to ffmpeg before the -i flag. If you are not sure what to use, leave this as default.
    leave_on_finish: :class:`bool`
        Whether or not to leave the voice channel when the queue finishes by itself
    leave_on_stop: :class:`bool`
        Whether or not to leave the voice channel when the queue is stopped manually
    save_previous_songs: :class:`bool`
        Whether or not to save the previous songs that played while the client is still in the voice channel
    Attributes
    ----------
    queues: :class:`list[Queue]`
        The list of `Queue`s that this instance is handling
    """
    def __init__(
        self,
        client: discord.Client,
        ytdl_options=YTDL_OPTIONS_DEFAULT,
        ffmpeg_options=FFMPEG_OPTIONS_DEFAULT,
        ffmpeg_before_options=FFMPEG_BEFORE_OPTIONS_DEFAULT,
        leave_on_finish: bool = True,
        leave_on_stop: bool = False,
        save_previous_songs: bool = True,
        join_new_voice_channel: bool = True
    ):
        self.client = client
        self.ytdl_options = ytdl_options
        self.ffmpeg_options = ffmpeg_options
        self.ffmpeg_before_options = ffmpeg_before_options
        self.leave_on_finish = leave_on_finish
        self.leave_on_stop = leave_on_stop
        self.save_previous_songs = save_previous_songs
        self.join_new_voice_channel = join_new_voice_channel

        self.queues: list[Queue] = []

    async def search(
        self,
        query: str,
        limit: int = 5,
        search_type: str = "video",
        member: discord.Member = None,
    ) -> Song | list[SearchResultVideo]:
        """
        Searches for an audio source through youtube.

        Parameters
        ----------
        query: :class:`str`
            The query you want to search with. A valid url can also be used and will result in a faster search.
        limit: :class:`int`
            If a url is NOT used, this will be the limit of youtube videos that will be returned when searching.
        search_type: :class:`str`
            Valid types are "video" or "playlist". Default is "video"
        member: :class:`Member`
            This discord member that searched for the audio source. Default is `None`

        Returns
        ---------
        :class:`Song`
            If a valid youtube url was queried, this will be returned. This can be used in the `play()` method
        :class:`list[SearchResultVideo]`
            If a non-url string was queried, a list of search results will be returned. This can be used in the `play()` method
        """

        if search_type == "video":

            is_url = re.match(URL_REGEX, query)

            if is_url:
                return [self.create_song(query, member)]
            else:
                search = VideosSearch(query, limit=limit)
                try:
                    results = search.result()["result"]
                    search_result_list = []
                    for x in results:
                        search_result = SearchResultVideo(x, member)
                        search_result_list.append(search_result)
                    return search_result_list
                except Exception as e:
                    raise e

    async def play(
        self,
        voice_channel: discord.VoiceChannel,
        source: Song | SearchResultVideo | str,
        text_channel: discord.TextChannel = None,
        position=-1,
    ):
        """
        Joins a voice channel and plays an audio source/song through a Discord client/bot.
        A song queue will be made and songs will be added and played one after the other, unless
        otherwise specified.

        Parameters
        ----------
        voice_channel: :class:`VoiceChannel`
            The voice channel that the client should join and play an audio source to.
        source: :class:`Song` | `SearchResultVideo` | `str`
            The audio source that will played to the voice channel. `Song` and `SearchResultVideo` must be obtained
            from the `search()` method. A valid youtube url can also be used
        text_channel: :class:`TextChannel`
            The text channel that the interaction, command or message came from. This can be used to keep messages from
            client or bot in the same channel for music interactions.
        position: :class:`int`
            The position in the `Queue` for this audio source to be put into. Default is -1, which will put the audio source at the end of the
            queue.
        """
        if type(source) == SearchResultVideo:
            source = await self.create_song(source.url, source.member)

        queue: Queue = await self.create_queue(
            voice_channel, source, text_channel, voice_channel.guild.id
        )

        await queue.add_to_queue(source, position)

        return True


    async def pause():
        pass

    async def resume():
        pass

    async def skip():
        pass

    async def stop():
        pass

    async def get_queue():
        pass

    async def jump():
        pass

    async def seek():
        pass

    async def set_volume(self, queue: Queue, volume: float):
        """
        Set the volume of audio sources for a guild's `Queue`

        Parameters
        ----------
        queue: :class:`Queue`
            The queue to set the volume for
        volume: :class:`float`
            The value to set the volume to. Must be a valid `float`
        """
        found = await self._is_queue_in_list(queue)

        if found:
            queue.volume = volume

    async def get_queue(self, guild_id: int = None):
        """
        Gets a guild's music `Queue`

        Parameters
        ----------
        guild_id: :class:`int`
            The `Guild`s id.

        Returns
        ----------
        :class:`Queue`
            If queues list is not empty and a queue was found
        :class:`None`
            If queue with `guild_id` was not found
        """
        if len(self.queues) > 0:
            for x in self.queues:
                if x.guild_id == guild_id:
                    return x

        return None
    
    async def _is_queue_in_list(self, queue: Queue) -> bool:
        return queue in self.queues

    async def create_queue(self, voice_channel, song, text_channel, guild_id):

        found = await self.get_queue(guild_id)

        if found != None:
            return found

        voice = DiscPyMusicVoice(voice_channel)
        queue = Queue(self, voice, song, text_channel, guild_id)
        self.queues.append(queue)
        return queue

    async def create_song(self, url, member=None) -> Song:
        """
        Builds a `Song` object with the supplied url
        """
        with YoutubeDL(self.ytdl_options) as ydl:
            info = ydl.extract_info(url, download=False)
            return Song(info, member)