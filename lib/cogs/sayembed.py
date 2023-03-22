from typing import Optional

import discord
from discord.ext.commands import Cog, command
from discord.utils import get


class SayEmbed(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="sayembed", hidden=True)
    async def say_embed_message(
        self,
        ctx,
        channelId: str = "",
        *,
        message: Optional[str] = "No message was given."
    ):
        channel_to_send = await self.bot.fetch_channel(int(channelId))

        if channel_to_send:
            role = get(self.bot.guild.roles, name="Support Developers")  # Get the role

            if role in ctx.author.roles:
                await channel_to_send.send(
                    embed=discord.Embed(
                        title="Notice from Team Swordphin",
                        description=message,
                        colour=0x5387B8,
                    )
                )
                await ctx.message.delete()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("sayembed")


async def setup(bot):
    await bot.add_cog(SayEmbed(bot))
