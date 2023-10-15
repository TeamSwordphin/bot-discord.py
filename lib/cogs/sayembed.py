import discord
from discord import TextChannel, app_commands
from discord.ext.commands import Cog


class SayEmbed(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="sayembed",
        description="Sends the following Embed message to a channel.",
    )
    @app_commands.describe(
        channel="The channel to send this message in.", message="The message to send."
    )
    @app_commands.guild_only()
    async def say_embed_message(
        self,
        interaction: discord.Interaction,
        channel: TextChannel,
        message: str,
    ):
        if channel:
            embedObj = discord.Embed(
                title="Notice from Team Swordphin", description=message, colour=0x5387B8
            )
            embedObj.set_image(url="https://i.imgur.com/JO4qyV8.png")
            embedObj.set_footer(
                text="These rules are subject to change. Developers and moderators have the right to moderate users for any activity that is considered to violate these rules. Punishments are discretionary (up to the moderator acting) and will often apply according to the situation's severity."
            )

            await channel.send(embed=embedObj)
            await interaction.response.send_message(
                f"Sent the embed! {interaction.user.mention}!"
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("sayembed")


async def setup(bot):
    await bot.add_cog(SayEmbed(bot))
