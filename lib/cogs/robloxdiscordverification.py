from ast import alias

import discord
import requests
from discord import Member, app_commands
from discord.ext.commands import Cog, command
from discord.utils import get

from ..db import db

TEXT_CHANNELS_TO_SEND = [734172216299880480, 410596271057797131]
SWORD_FISH_CLUB_ID = 3451727


def can_send_in_channel(channelID):
    for channelInfo in TEXT_CHANNELS_TO_SEND:
        if channelInfo == channelID:
            return True
    return False


class Verification(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_updated = ""

    async def get_json(self, link):
        response = requests.get(link)
        return response.json()

    async def update_db(self):
        # Create Verification table for existing users
        db.multiexecute(
            "INSERT OR IGNORE INTO robloxverification (UserID) VALUES (?)",
            ((member.id,) for member in self.bot.guild.members if not member.bot),
        )

        # Remove verification from left members
        to_remove = []
        stored_members = db.column("SELECT UserID FROM robloxverification")
        for id_ in stored_members:
            if not self.bot.guild.get_member(id_):
                to_remove.append(id_)
        db.multiexecute(
            "DELETE FROM robloxverification WHERE UserID = ?",
            ((id_,) for id_ in to_remove),
        )
        db.commit()

    @app_commands.command(
        name="verifyme",
        description="Begin the verification process.",
    )
    @app_commands.describe(userid="Your Roblox User Id to use for verification.")
    async def say_verification(
        self, interaction: discord.Interaction, userid: str
    ) -> None:
        if can_send_in_channel(interaction.channel.id):
            if userid != None:
                json = await self.get_json(
                    f"https://users.roblox.com/v1/users/{userid}"
                )
                if json.get("id"):
                    strCount = json["description"].find("!verifyme")
                    if strCount != -1:
                        # Check if they are in the group
                        groupJson = await self.get_json(
                            f"https://groups.roblox.com/v1/users/{userid}/groups/roles"
                        )
                        inGroup = False

                        for groupInfo in groupJson["data"]:
                            group = groupInfo.get("group")
                            if group:
                                groupId = group.get("id")
                                if groupId:
                                    if groupId == SWORD_FISH_CLUB_ID:
                                        inGroup = True

                        db.execute(
                            "UPDATE robloxverification SET RobloxProfileLink = ? WHERE UserID = ?",
                            userid,
                            interaction.user.id,
                        )
                        db.commit()

                        if inGroup:
                            await interaction.user.add_roles(
                                get(self.bot.guild.roles, name="Swordfish Club")
                            )
                            print("GAVE SWORDFISH ROLE!!")
                        else:
                            await interaction.user.add_roles(
                                get(self.bot.guild.roles, name="Not in the club")
                            )
                            print("NOT IN THE CLUB ROLE!!")

                        bot_channel = await self.bot.fetch_channel(410596271057797131)
                        await interaction.user.edit(nick=json.get("name"))
                        await bot_channel.send(
                            f"{interaction.user.mention} was verified from Roblox User ID {userid}"
                        )

                        await interaction.response.send_message(
                            f"{interaction.user.mention} is verified."
                        )

                    else:
                        await interaction.response.send_message(
                            f"Found your Roblox Profile {interaction.user.mention}! Please follow the instructions below to continue verification:"
                        )
                        description = """**Step 1**
						Please go to your Roblox Profile, edit your User Profile's description to include the tag "!verifyme".

						**Step 2**
						Come back here, and type in "/verifyme YOUR_USER_ID_HERE" again.

						**Step 3**
						You may remove this tag once verification is complete.
						"""

                        embedObj = discord.Embed(
                            title="Verification Pt.2",
                            description=description,
                            colour=0x5387B8,
                        )
                        await interaction.channel.send(embed=embedObj)
                        await interaction.channel.send(
                            "https://i.imgur.com/Aa57Gr8.mp4"
                        )

                else:
                    await interaction.response.send_message(
                        f"Hi {interaction.user.mention}, I did not find a user that goes under the id of **{userid}**! Please make sure the id you gave is correct."
                    )
            else:
                await interaction.response.send_message(
                    f"Please follow the instructions below to verify yourself:"
                )
                description = """Please use the command /verifyme followed by the UserId of your Roblox Profile. For example:

				**/verifyme YOUR_USER_ID_HERE**
				**/verifyme 297701**

				To find your UserId, please go to your Roblox profile, and copy the numbers from the URL bar:
				"""

                embedObj = discord.Embed(
                    title="Verification Instructions",
                    description=description,
                    colour=0x5387B8,
                )
                embedObj.set_image(url="https://i.imgur.com/81H6jxP.png")
                await interaction.channel.send(embed=embedObj)

    @app_commands.command(
        name="setprofile",
        description="Connect a Discord member to a Roblox profile.",
    )
    @app_commands.describe(
        member="The member to set.",
        userid="Your Roblox User Id to use for verification.",
    )
    async def set_roblox_profile(
        self, interaction: discord.Interaction, member: Member, userid: str
    ) -> None:
        if member != None:
            roleMod = get(self.bot.guild.roles, name="Moderator")  # Get the role
            roleSup = get(self.bot.guild.roles, name="Support Developers")

            if roleMod in interaction.user.roles or roleSup in interaction.user.roles:
                json = await self.get_json(
                    f"https://users.roblox.com/v1/users/{userid}"
                )
                if json.get("id"):
                    db.execute(
                        "UPDATE robloxverification SET RobloxProfileLink = ? WHERE UserID = ?",
                        userid,
                        member.id,
                    )
                    db.commit()
                    name = json.get("name")
                    await interaction.response.send_message(
                        f"{member.mention} profile set to {name}. Remember to manually set their nickname if applicable."
                    )
                else:
                    await interaction.response.send_message(
                        f"Could not find Roblox Profile with userid {userid}"
                    )
        else:
            await interaction.response.send_message("You must also specify a member.")

    async def get_roblox_id(self, member: Member = None):
        link = db.record(
            "SELECT RobloxProfileLink FROM robloxverification WHERE UserID = ?",
            member.id,
        )

        if link != None:
            return "".join(link)

    @app_commands.command(
        name="verifyprofile",
        description="Verify a member's Roblox Profile.",
    )
    @app_commands.describe(member="The member to verify.")
    async def verify_roblox_profile(
        self, interaction: discord.Interaction, member: Member
    ) -> None:
        id = None
        if member != None:
            id = await self.get_roblox_id(member)
        else:
            id = await self.get_roblox_id(interaction.user)

        if id != None:
            await interaction.response.send_message(
                f"https://www.roblox.com/users/{id}/profile"
            )
        else:
            await interaction.response.send_message(
                "This user's Roblox Profile was not found."
            )

    @app_commands.command(
        name="gettesters",
        description="Returns a list of all current P3 Testers.",
    )
    async def getuser(self, interaction: discord.Interaction) -> None:
        roleSup = get(self.bot.guild.roles, name="Support Developers")
        if roleSup in interaction.user.roles:
            empty = True
            roleTester = get(self.bot.guild.roles, name="Cubicle Office Worker")

            # Get all objects, and combine them into a bulletpointed list
            list = ""
            for member in self.bot.guild.members:
                if roleTester in member.roles:
                    link = db.record(
                        "SELECT RobloxProfileLink FROM robloxverification WHERE UserID = ?",
                        member.id,
                    )
                    id = ""

                    try:
                        id = "".join(link)
                    except:
                        list = list + f"• {member.name} does not have a UserId set.\n"
                    else:
                        json = await self.get_json(
                            f"https://users.roblox.com/v1/users/{id}"
                        )
                        if json.get("id"):
                            name = json.get("name")
                            list = (
                                list
                                + f"• {member.mention} is set to [{name}] with UserId **{id}**.\n"
                            )
                            empty = False
                        else:
                            list = (
                                list + f"• {member.name} does not have a UserId set.\n"
                            )

            if empty:
                await interaction.response.send_message(
                    f"Nobody has the role {roleTester.name}"
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Tester Roblox Profiles",
                        description=list,
                        colour=0x5387B8,
                    )
                )

    # Ping the user for verification instructions
    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO robloxverification (UserID) VALUES (?)", member.id)
        verification_channel = await self.bot.fetch_channel(734172216299880480)
        await verification_channel.send(
            f"{member.mention} Welcome to the Official Team Swordphin Discord!"
        )

        description = """Please use the command /verifyme followed by the UserId of your Roblox Profile. For example:

        **/verifyme YOUR_USER_ID_HERE**
        **/verifyme 297701**

        To find your UserId, please go to your Roblox profile, and copy the numbers from the URL bar:
        """

        embedObj = discord.Embed(
            title="How to Verify Yourself", description=description, colour=0x5387B8
        )
        embedObj.set_image(url="https://i.imgur.com/81H6jxP.png")
        await verification_channel.send(embed=embedObj)

    # Delete to databases
    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM robloxverification WHERE UserID = ?", member.id)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            await self.update_db()
            self.bot.ready_cogs.ready("robloxdiscordverification")


async def setup(bot):
    await bot.add_cog(Verification(bot))
