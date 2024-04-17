import asyncio
from typing import Self

import discord
from errors import DiscPyMusicError
from song import Song
from voice import DiscPyMusicVoice
from yt_dlp import YoutubeDL


class Queue:
    """
    Represents a song/music queue. Handles playing, pausing and stopping audio sources through a discord client/bot
    This class is not meant to be instantiated on its own.

    Parameters
    -----------
    discpymusic: :class:`DiscPyMusic`
        The instance of `DiscPyMusic` that this should be tied to
    voice: :class: `DiscPyMusicVoice`
        The `DiscPyMusicVoice` that should be used for the instance
    first_song: :class:`Song`
        The first song that should be added to the queue
    text_channel: :class:`TextChannel`
        A discord.py text channel
    guild_id: :class:`int`
        The guild id that should be tied to this instance

    Attributes
    ----------
    songs: :class:`list[Song]`
        The list of songs in the queue
    previous_songs: :class:`list[Song]`
        A list of songs that have already been played for this queue
    playing: :class:`bool`
        If this queue is currently playing an audio source or not
    paused: :class:`bool`
        If this queue is currently paused or not
    now_playing: class:`Song`
        The song that is currently playing in the queue
    self.volume: class:`float`
        The volume for audio sources in the queue. Default is `0.5`
    """

    def __init__(
        self,
        discpymusic,
        voice: DiscPyMusicVoice,
        first_song: Song,
        text_channel: discord.TextChannel,
        guild_id,
    ):
        self.discpymusic = discpymusic
        self.guild_id = guild_id
        self.voice: DiscPyMusicVoice = voice
        self.songs: list[Song] = [first_song]
        self.previous_songs: list[Song] = []
        self.playing: bool = False
        self.paused: bool = False
        self.now_playing: Song = None
        self.text_channel: discord.TextChannel = text_channel
        self.volume: float = 0.5

    async def add_to_queue(self, song: Song, position=-1) -> list[Song]:
        """
        Add a song to this queue. Can be put into a certain position of the queue, too.
        """

        if position > -1:
            self.songs.insert(position, song)
        else:
            self.songs.append(song)

        if not self.playing and not self.paused:
            await self.play()

        return self.songs

    async def play(self):
        """
        Handles playing of audio sources. Uses client's async loop to continuously play songs that are in the queue.
        Also handles logic like adding songs to the `previous_songs` list and changes the `now_playing` song.
        """
        if len(self.songs) > 0:
            url = self.songs[0].url

            #Make sure client is connected to a voice channel. If not, try to connect.
            await self.ensure_voice()

            self.playing = True
            self.now_playing = self.songs[0]
            self.previous_songs.append(self.songs[0])
            self.songs.pop(0)

            loop = asyncio.get_event_loop()

            with YoutubeDL(self.discpymusic.ytdl_options) as ydl:
                data = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )
                song = data["url"]

                audio_source = discord.FFmpegPCMAudio(
                    source=song,
                    before_options=self.discpymusic.ffmpeg_before_options,
                    options=self.discpymusic.ffmpeg_options,
                )

                #To be able to change volume
                volume_transform = discord.PCMVolumeTransformer(
                    audio_source, self.volume
                )

                self.voice.voice_client.play(
                    volume_transform,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play(), self.discpymusic.client.loop
                    ),
                )
        else:
            #If queue is empty then stop playing audio and leave the voice channel
            await self.voice.voice_client.stop()
            await self.voice.voice_client.disconnect()

    async def ensure_voice(self):
        """
        Ensures client/bot is connected to a voice channel. Tries to connect to voice if not connected
        """

        if (
            self.voice.voice_client == None
            or not self.voice.voice_client.is_connected()
        ):
            await self.voice.join()
            return True
