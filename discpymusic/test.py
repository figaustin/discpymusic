import os

import discord
from discord import app_commands
from dotenv import load_dotenv
from discpymusic.discpymusic import DiscPyMusic

load_dotenv()
token = str(os.getenv("TOKEN"))

intents = discord.Intents.default()
intents.message_content = True


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


client = MyClient(intents=intents)

@client.tree.command(name="test")
async def test_command(interaction: discord.Interaction):
    await interaction.response.defer()
    disc = DiscPyMusic(client=client)
    songs = await disc.search("tool sober", limit=2, return_obj="song")

    song = songs[0]
    await disc.play(interaction.user.voice.channel, song, interaction.channel)

    await interaction.followup.send("Worked!")


async def try_this():
    disc = DiscPyMusic(client=client)

    songs = await disc.search("feint", return_obj="search")

    print(songs)


client.run(token)
