import discord
from discord import app_commands
from discord.ext.commands import Cog


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to Althea!")
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("fun")


async def setup(bot):
    await bot.add_cog(Fun(bot))
