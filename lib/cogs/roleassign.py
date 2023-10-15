import discord
from discord import TextChannel, app_commands
from discord.ext.commands import Cog, command
from discord.utils import get

emojis = [586372671646728193, 586724160244285440]


class RoleAssign(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_listener_message_id = 738493435853406301

    @command(name="editMessage", aliases=["edit"])
    async def edit_role_messages(self, ctx, channelId: str = ""):
        roleSup = get(self.bot.guild.roles, name="Developers")

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

    @app_commands.command(
        name="postlinkedrolemessage",
        description="Post linked role instructions.",
    )
    @app_commands.describe(
        channel="The channel to send it to.",
    )
    @app_commands.guild_only()
    async def post_linked_role(
        self, interaction: discord.Interaction, channel: TextChannel
    ) -> None:
        titleRule = "Linked Roles - BETA"
        descRule = f"""Some channels may require increased verification in order to interact with. Currently <#383970940448538625> is the only channel locked behind this step to prevent bots but we are planning to add more exclusive, fun developer channels in the future for people with Linked Roles.

        Connecting your account to Linked role(s) rewards the following:

        <:TSPaltheaWave:733842618533937213> **Champion Role**
        Replace your current chat color with a nicer, light blue hue.

        <:TSPclydeeyebrowraise:1062496580353142844> **Exclusive Channel(s)**
        For now, only <#383970940448538625> is locked to participants with a Linked Role. We are planning on rolling out fun developer channels, bot commands, and more to these users with the role so stay tuned!

        <:TSPlfDab:665117519127773196> **Stats at a glance**
        Show off your in-game achievements on your Discord profile to other users! This feature only appears in this server. See images below on what this looks like!
        """

        embedObj = discord.Embed(title=titleRule, description=descRule, colour=0x5387B8)
        await channel.send(embed=embedObj)

        titleRule2 = "How To Get a Linked Role"
        descRule2 = f"""There will be images below this post in case you get stuck.
        
        **1. Ensure you have launched PWNED 3 at least once, in a server that is at least version 1.5**
        This ensures that your save has the most up-to-date file structure for Althea to look with.

        **2. Go to the top left, click the Server Name, then Click on Linked Roles**

        **3. Choose the Linked Role(s) you want to apply to. Follow the on-screen instructions.**
        This feature is still in early infancy, so there may be bugs related to the verification process. If something goes wrong, please try again later.

        **4. Ensure you have the Linked Role(s) and Stats on your Discord Profile.**
        Stats do not update in real-time. They update only when you run the </character:1087913261648846978>. See Troubleshooting below.
        
        **TROUBLESHOOTING: The bot will not update / I do not meet the requirements** 
        If you know you have the stats in-game but the bot isn't updating, try running </character:1087913261648846978> on yourself. Any character choice will do. If you are not Level 75 yet in the Discord, get someone else who is to do that for you. This will force the bot to update your stats in the discord.
        """

        embedObj2 = discord.Embed(
            title=titleRule2, description=descRule2, colour=0x5387B8
        )
        embedObj2.set_image(url="https://i.imgur.com/Hzha6Wj.png")
        embedObj2.set_footer(
            text="These are not member roles and will not give access to any text channels by default. You must use the appropriate verification channels."
        )
        await channel.send(embed=embedObj2)
        await channel.send("https://imgur.com/Y8SAmhf")
        await channel.send("https://imgur.com/u64ymOf")

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


async def setup(bot):
    await bot.add_cog(RoleAssign(bot))
