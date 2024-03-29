from datetime import datetime, timedelta
from random import randint

import discord
from discord import Member, app_commands
from discord.ext.commands import Cog, command
from discord.utils import get

from ..db import db

CHANNEL_EXP = [
    {"ChannelID": 311202522922614794, "EXP": 20},  # General
    {"ChannelID": 410995977688842240, "EXP": 10},  # Pwned-Series
    {"ChannelID": 328213599501680641, "EXP": 10},  # help-questions
    {"ChannelID": 902333857112674305, "EXP": 5},  # trading
    {"ChannelID": 906731177795285053, "EXP": 5},  # lfg
    {"ChannelID": 410596428348391445, "EXP": 5},  # high-class
    {"ChannelID": 734153525289943130, "EXP": 10},  # mute-vc
    {"ChannelID": 410983771773599745, "EXP": 200},  # test channel
]


def get_xp_amount(channelID):
    for channelInfo in CHANNEL_EXP:
        if channelInfo["ChannelID"] == channelID:
            return channelInfo["EXP"]


def adjust_lvl(xp):
    return int((xp // 42) ** 0.55)


class XP(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message, addBonusXp):
        xp, lvl, xplock = db.record(
            "SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id
        )
        # print(xp, lvl, xplock)

        if addBonusXp > 0 or datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl, addBonusXp)

    async def add_xp(self, message, xp, lvl, addBonusXp):
        fetch_xp = get_xp_amount(message.channel.id)

        if fetch_xp is None:
            return

        xp_to_add = randint(fetch_xp - 5, fetch_xp + 5) + addBonusXp
        new_lvl = adjust_lvl(xp + xp_to_add)

        db.execute(
            "UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
            xp_to_add,
            new_lvl,
            (datetime.utcnow() + timedelta(seconds=60)).isoformat(),
            message.author.id,
        )
        db.commit()

        # Grant image perms
        gotImgPerm = False
        if new_lvl == 25:
            gotImgPerm = True
            await message.author.add_roles(get(self.bot.guild.roles, name="chat perms"))

        if new_lvl > lvl:
            async with message.channel.typing():
                if gotImgPerm == True:
                    await message.channel.send(
                        "Congrats {}! You reached Level {}! You now have permission to post embed links and attach files!".format(
                            message.author.mention, new_lvl
                        )
                    )
                else:
                    await message.channel.send(
                        "Congrats {}! You reached Level {}!".format(
                            message.author.mention, new_lvl
                        )
                    )

    async def get_stats(self, target):
        return db.record("SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (
            None,
            None,
        )

    async def display_level(self, interaction: discord.Interaction, target):
        xp, lvl = await self.get_stats(target)
        async with interaction.channel.typing():
            if xp:
                await interaction.response.send_message(
                    "{} is on Level {} with {} XP.".format(target.display_name, lvl, xp)
                )
            else:
                await interaction.response.send_message(
                    "This member does not have a level."
                )

    async def update_db(self):
        # Create XP for existing users
        db.multiexecute(
            "INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
            ((member.id,) for member in self.bot.guild.members if not member.bot),
        )

        # Remove XP from left members
        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.bot.guild.get_member(id_):
                to_remove.append(id_)
        db.multiexecute(
            "DELETE FROM exp WHERE UserID = ?", ((id_,) for id_ in to_remove)
        )
        db.commit()

    @app_commands.command(
        name="level",
        description="Shows the Discord Level of a member.",
    )
    @app_commands.describe(member="The member to show.")
    async def say_level(self, interaction: discord.Interaction, member: Member) -> None:
        if member != None:
            await self.display_level(interaction, member)
        else:
            await self.display_level(interaction, interaction.user)

    @app_commands.command(
        name="setxp",
        description="Set the XP of a specified member.",
    )
    @app_commands.describe(
        member="The member to set the xp for.",
        exp="The EXP that this user will be set to.",
    )
    @app_commands.guild_only()
    async def addexp(
        self, interaction: discord.Interaction, member: Member, exp: str
    ) -> None:
        if member != None:
            role = get(self.bot.guild.roles, name="Developers")  # Get the role
            if role in interaction.user.roles:
                amount = int(exp)
                new_lvl = adjust_lvl(amount)

                db.execute(
                    "UPDATE exp SET XP = ?, Level = ?, XPLock = ? WHERE UserID = ?",
                    amount,
                    new_lvl,
                    (datetime.utcnow() + timedelta(seconds=60)).isoformat(),
                    member.id,
                )
                db.commit()

                await interaction.response.send_message(
                    f"Changed {member.mention}'s XP to {exp}!"
                )
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} Please indicate a user to change xp!"
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            await self.update_db()
            self.bot.ready_cogs.ready("xp")

    # Write to databases
    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)

    # Delete to databases
    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE UserID = ?", member.id)

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message, 0)


async def setup(bot):
    await bot.add_cog(XP(bot))
