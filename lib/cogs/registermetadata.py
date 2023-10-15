import json

import discord
import requests
from discord import app_commands
from discord.ext.commands import Cog

body = [
    {
        "key": "hoursplayed",
        "name": "Hours Played",
        "description": "Hours Played Greater Than",
        "type": 2,
    },
    {
        "key": "totalenemieskilled",
        "name": "Total Kills",
        "description": "Total Killed Greater Than",
        "type": 2,
    },
    {
        "key": "dungeonscompleted",
        "name": "Dungeons Completed",
        "description": "Dungeons Completed Greater Than",
        "type": 2,
    },
    {
        "key": "highestcombo",
        "name": "Highest Combo",
        "description": "Combo Greater Than",
        "type": 2,
    },
    {
        "key": "verified",
        "name": "Verified",
        "description": "Is Verified",
        "type": 7,
    },
]


class RegisterMetadata(Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("./lib/bot/bot_client_id.0", "r", encoding="utf-8") as tokenFile:
            self.client_id = tokenFile.read()

    @app_commands.command(name="sendmetadata", description="Sends metadata to Discord.")
    @app_commands.guild_only()
    async def sendmetadata(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Metadata was already sent! {interaction.user.mention}!"
        )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("registermetadata")


async def setup(bot):
    await bot.add_cog(RegisterMetadata(bot))
