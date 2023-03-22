from typing import Optional

import discord
from discord import Member, app_commands
from discord.ext.commands import Cog
from discord.utils import get

from ..db import db


class Warn(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_db(self):
        # Remove warnings from left members
        to_remove = []
        stored_members = db.column("SELECT UserID FROM warnlog")
        for id_ in stored_members:
            if not self.bot.guild.get_member(id_):
                to_remove.append(id_)
        db.multiexecute(
            "DELETE FROM warnlog WHERE UserID = ?", ((id_,) for id_ in to_remove)
        )
        db.commit()

    @app_commands.command(
        name="strike", description="Give a user a strike! Only available to moderators."
    )
    @app_commands.describe(
        member="Choose a member to strike.",
        warning="The reason for this strike.",
    )
    async def record_warning(
        self,
        interaction: discord.Interaction,
        member: Member,
        *,
        warning: str,
    ) -> None:
        if member != None:
            roleMod = get(self.bot.guild.roles, name="Moderator")  # Get the role
            roleSup = get(self.bot.guild.roles, name="Support Developers")

            if roleMod in interaction.user.roles or roleSup in interaction.user.roles:
                db.execute(
                    "INSERT INTO warnlog (UserID, Reason) VALUES (?, ?)",
                    member.id,
                    warning,
                )
                db.commit()

                title = f"{member.name} has been given a strike!"
                desc = warning
                await interaction.response.send_message(
                    embed=discord.Embed(title=title, description=desc, colour=0x5387B8)
                )

    @app_commands.command(
        name="getstrikes",
        description="Shows a list of all strikes a user has collected.",
    )
    @app_commands.describe(member="The member to see their strikes.")
    async def get_warnings(
        self, interaction: discord.Interaction, member: Member
    ) -> None:
        if member != None:
            roleMod = get(self.bot.guild.roles, name="Moderator")  # Get the role
            roleSup = get(self.bot.guild.roles, name="Support Developers")

            if roleMod in interaction.user.roles or roleSup in interaction.user.roles:
                reasons = db.records(
                    "SELECT Reason FROM warnlog WHERE UserID = ?", member.id
                )
                strikeNo = 1

                await interaction.response.send_message(
                    f"Getting strikes for {member.mention}..."
                )

                for reason in reasons:
                    title = f"Strike {str(strikeNo)}"
                    desc = "".join(reason)
                    strikeNo += 1

                    await interaction.channel.send(
                        embed=discord.Embed(
                            title=title, description=desc, colour=0x5387B8
                        )
                    )

    @app_commands.command(
        name="resetstrikes",
        description="Purges all strikes accumulated on a chosen user.",
    )
    @app_commands.describe(member="The member to reset the strikes for.")
    async def reset_strikes(
        self, interaction: discord.Interaction, member: Member
    ) -> None:
        if member != None:
            roleMod = get(self.bot.guild.roles, name="Moderator")  # Get the role
            roleSup = get(self.bot.guild.roles, name="Support Developers")

            if roleMod in interaction.user.roles or roleSup in interaction.user.roles:
                db.execute("DELETE FROM warnlog WHERE UserID = ?", member.id)
                await interaction.response.send_message(
                    f"{member.mention} strikes has been reset."
                )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            await self.update_db()
            self.bot.ready_cogs.ready("warnsystem")

    # Delete to databases
    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM warnlog WHERE UserID = ?", member.id)


async def setup(bot):
    await bot.add_cog(Warn(bot))
