import discord
from discord.ext.commands import Cog, command
from discord.utils import get

emojis = [586372671646728193, 586724160244285440]


class RoleAssign(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_listener_message_id = 738493435853406301

    @command(name="editMessage", aliases=["edit"])
    async def edit_role_messages(self, ctx, channelId: str = ""):
        roleSup = get(self.bot.guild.roles, name="Support Developers")

        if roleSup in ctx.author.roles:
            channel = await self.bot.fetch_channel(int(channelId))
            message = await channel.fetch_message(self.role_listener_message_id)

            if message:
                titleRule = "Role Assignments"
                descRule = """React with any of the following emojis to give yourself a ping role. Unreact at any time to remove the role.

							{} **Ping for Development News**: 
							React if you would like to get pinged for important development news or releases regarding Team Swordphin's projects. Updates to the game will use this role regularly.
							
							{} **Ping for Community Events**: 
							React if you would like to get pinged for commmunity related events for Discord and in-game.
							""".format(
                    "<:TSPalburnPinged:586724160244285440>",
                    "<:TSPshopkeepEZ:586372671646728193>",
                )

                embedObj = discord.Embed(
                    title=titleRule, description=descRule, colour=0x5387B8
                )

                embedObj.set_image(url="https://i.imgur.com/PUbSYro.png")
                embedObj.set_footer(
                    text="These are not member roles and will not give access to any text channels by default. To see community chat channels, you must use the appropriate verification channels."
                )

                await message.edit(embed=embedObj)
            else:
                await ctx.channel.send(
                    "{} This message does not exist.".format(ctx.author.mention)
                )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("roleassign")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id is None or self.role_listener_message_id is None:
            return

        # 	message = await channel.fetch_message(payload.message_id)
        tspServer = self.bot.guild
        emoji = payload.emoji

        if payload.message_id == self.role_listener_message_id:
            if emoji.id == emojis[1]:  # Alburn ping
                await payload.member.add_roles(tspServer.get_role(606755292520382466))
                await payload.member.send(
                    "You now have the Pin role! Prepared to be pinged, {}! You can remove the role any time by unreacting.".format(
                        payload.member.mention
                    )
                )
            elif emoji.id == emojis[0]:  # Shopkeeper ping
                await payload.member.add_roles(tspServer.get_role(1069686034339733514))
                await payload.member.send(
                    "You now have the Community Stoof role! Prepared to be pinged for any community related events, {}! You can remove the role any time by unreacting.".format(
                        payload.member.mention
                    )
                )

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id is None or self.role_listener_message_id is None:
            return

        tspServer = self.bot.guild
        emoji = payload.emoji

        if payload.message_id == self.role_listener_message_id:
            if emoji.id == emojis[1]:
                member = await tspServer.fetch_member(payload.user_id)
                await member.remove_roles(tspServer.get_role(606755292520382466))
                await member.send(
                    "Sorry to see you go! I have removed your pin role, {}. You will no longer be pinged for any future important news relating to the development of PWNED!".format(
                        member.mention
                    )
                )
            elif emoji.id == emojis[0]:
                member = await tspServer.fetch_member(payload.user_id)
                await member.remove_roles(tspServer.get_role(1069686034339733514))
                await member.send(
                    "Sorry to see you go! I have removed your community stoof role, {}. You will no longer be pinged for future community related events!".format(
                        member.mention
                    )
                )


def setup(bot):
    bot.add_cog(RoleAssign(bot))
