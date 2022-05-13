from discord.ext.commands import Cog, command
from discord.utils import get

class RoleAssign(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.role_listener_message_id = 738493435853406301

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.ready_cogs.ready("roleassign")

	@Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.guild_id is None or self.role_listener_message_id is None:
			return

		channel = await self.bot.fetch_channel(payload.channel_id)
	#	message = await channel.fetch_message(payload.message_id)
		tspServer = self.bot.guild
		emojis = [586372671646728193, 586724160244285440]
		emoji = payload.emoji

		if payload.message_id == self.role_listener_message_id:
		#	await message.author.add_roles(get(tspServer.roles, name="Swordfish Club"))
		#	if emoji.id == emojis[0]: # Shopkeeper kool
		#		await payload.member.remove_roles(get(tspServer.roles, name="Swordfish Club"), get(tspServer.roles, name="Not in the club"))
		#		await payload.member.send("Hi {}! Please paste your roblox profile link here so I can see if you are in the group! "
		#								"The URL should look like this:\n\n**https://www.roblox.com/users/USER_ID_HERE/profile**"
		#								.format(payload.member.mention))
			if emoji.id == emojis[1]: # Alburn ping
				await payload.member.add_roles(get(tspServer.roles, name="PING ME"))
				await payload.member.send("You now have the Pin role! Prepared to be pinged, {}! You can remove the role any time by unreacting.".format(payload.member.mention))

	@Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if payload.guild_id is None or self.role_listener_message_id is None:
			return

		tspServer = self.bot.guild
		emoji = payload.emoji

		if payload.message_id == self.role_listener_message_id:
			if emoji.id == 586724160244285440:
				member = await tspServer.fetch_member(payload.user_id)
				await member.remove_roles(get(tspServer.roles, name="PING ME"))
				await member.send("Sorry to see you go! I have removed your pin role, {}.".format(member.mention))

def setup(bot):
	bot.add_cog(RoleAssign(bot))