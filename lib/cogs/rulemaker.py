import discord
from discord import app_commands
from discord.ext.commands import Cog, command
from discord.utils import get


class RuleMaker(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="newrules", aliases=["ruleupdate"], hidden=True)
    async def new_rule_notifier(self, ctx, channelId: str = ""):
        roleSup = get(self.bot.guild.roles, name="Developers")

        if roleSup in ctx.author.roles:
            channel = await self.bot.fetch_channel(int(channelId))

            titleRule = "Updated Server Rules"
            descRule = """The Team Swordphin's Discord **Server Rules** has been updated. Please make sure to read it over to make sure you are up to date. Failure to properly inform yourself of the updated rules can result in mutes, kicks, or bans.

            There is now a new ping role for community related events in #role-assignments!
						"""

            embedObj = discord.Embed(
                title=titleRule, description=descRule, colour=0x5387B8
            )
            embedObj.set_image(url="https://i.imgur.com/JO4qyV8.png")
            embedObj.set_footer(
                text="These rules are subject to change. Developers and moderators have the right to moderate users for any activity that is considered to violate these rules. Punishments are discretionary (up to the moderator acting) and will often apply according to the situation's severity."
            )

            await channel.send(embed=embedObj)

    @app_commands.command(
        name="postruleedits",
        description="Edits the hard-coded rules of this discord.",
    )
    @app_commands.guild_only()
    async def say_rules(self, interaction: discord.Interaction):
        roleSup = get(self.bot.guild.roles, name="Developers")

        if roleSup in interaction.user.roles:
            # Call this function every time we need to update the rules.
            channel = await self.bot.fetch_channel(311200318895423499)
            messageBan = await channel.fetch_message(921241612238094427)
            messageRules = await channel.fetch_message(921241612724625418)

            titleLink = "Ban Appeals & Scam Links"
            descLink = """**1. Scam Links**
						Please do not fall for scam links. If your account is compromised, it is likely your account was turned into a spam bot. If your account posts a scam link in any of our chat channels, it will result in an immediate ban.

						**2. Ban Appeals**
						For Discord ban appeals, please seek the moderators.
						"""

            embedObjLink = discord.Embed(
                title=titleLink, description=descLink, colour=0x5387B8
            )
            embedObjLink.set_thumbnail(url="https://i.imgur.com/P8lb5H7.png")
            await messageBan.edit(embed=embedObjLink)

            titleRule = "Server Rules"
            descRule = """**Be respectful.**
						Encourage meaningful discussion. Discussions, debates and media should remain respectful, civil, on topic and all-ages-appropriate. Don't bring outside issues to the Discord.
						
						**Keep content and discussions within the appropriate channels.**
						Avoid going off-topic. Please stick to the channel topic you are currently in. Any help questions must be kept in #help-questions. If you are in a voice channel, all text conversations and content must be kept in #mute-vc-club. Do not use any channels in contributions-&-bugs for casual conversations.

						**Avoid spamming and flooding chat.**
						This includes shit posting, image/emoji spam, being obnoxious in voice calls, using AltheaBot in the wrong channels, and advertising other Discords.

						**Do not discuss topics that directly violate Roblox's Community Guidelines.**
						This is a Roblox server. NSFW and derogatory words/slurs are prohibited and will be met with an instant ban. If you are unsure if something is NSFW or not, don't post it. Clarify with a moderator or Community Manager beforehand.

						**Name should be mentionable (using the @ symbol).**
                        Self-explanatory. You will be kicked if names aren't easily mentionable.

						**Avoid bypassing the filter.** 
						We use Discord's built-in automod feature to filter out controversial/inappropriate words and slurs. It's not intrusive for the most part, so follow this filter, and do not work around it.
						
						**Do not evade punishments.**
						Evading punishments in any way will result in a harsher punishment.

                        **Avoid posting appeals or posts made on behalf or about banned members.**
                        The banned member (both Discord and in-game) must go through the official communication channels (Community Manager, Moderators, or Dyno upon being banned) for appealing. We will not accept appeals done or asked by users who are not the original banned member. Talking about banned members, posting content or sharing posts made by banned members will also not be tolerated. This is to prevent members from acting as a "messenger" for banned users.
						"""

            embedObj = discord.Embed(
                title=titleRule, description=descRule, colour=0x5387B8
            )
            embedObj.set_image(url="https://i.imgur.com/JO4qyV8.png")
            embedObj.set_footer(
                text="These rules are subject to change. Developers and moderators have the right to moderate users for any activity that is considered to violate these rules. Punishments are discretionary (up to the moderator acting) and will often apply according to the situation's severity."
            )

            await messageRules.edit(embed=embedObj)
            await interaction.response.send_message(
                f"Edited the rules messages! {interaction.user.mention}!"
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("rulemaker")


async def setup(bot):
    await bot.add_cog(RuleMaker(bot))
