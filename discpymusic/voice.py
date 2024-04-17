import discord


class DiscPyMusicVoice:
    def __init__(self, voice_channel: discord.VoiceChannel):
        self.voice_channel = voice_channel
        self.voice_client: discord.VoiceClient = None
        self.self_deafen = False
        self.self_mute = False
        self.playback_duration = None

    async def join(self):
        self.voice_client = await self.voice_channel.connect(self_deaf=self.self_deafen, self_mute=self.self_mute)

    async def leave(self):
        await self.voice_client.disconnect(force=True)
        

