from datetime import datetime, timedelta
from random import randint
from ..db import db

from discord import Member
from discord.ext.commands import Cog, command
from discord.utils import get


CHANNEL_EXP = [
	{
		"ChannelID" : 311202522922614794, #General
		"EXP" : 20
	},
	{
		"ChannelID" : 410995977688842240, #Pwned-Series
		"EXP" : 10
	},
	{
		"ChannelID" : 328213599501680641, #help-questions
		"EXP" : 10
	},
	{
		"ChannelID" : 902333857112674305, #trading
		"EXP" : 5
	},
	{
		"ChannelID" : 906731177795285053, #lfg
		"EXP" : 5
	},
	{
		"ChannelID" : 410596428348391445, #high-class
		"EXP" : 5
	},
	{
		"ChannelID" : 734153525289943130, #mute-vc
		"EXP" : 10
	},
]

def get_xp_amount(channelID):
	for channelInfo in CHANNEL_EXP:
		if channelInfo["ChannelID"] == channelID:
			return channelInfo["EXP"]

class XP(Cog):
	def __init__(self, bot):
		self.bot = bot

	async def process_xp(self, message, addBonusXp):
		xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)
		#print(xp, lvl, xplock)

		if addBonusXp > 0 or datetime.utcnow() > datetime.fromisoformat(xplock):
			await self.add_xp(message, xp, lvl, addBonusXp)

	async def add_xp(self, message, xp, lvl, addBonusXp):
		fetch_xp = get_xp_amount(message.channel.id)

		if fetch_xp is None:
			return

		xp_to_add = randint(fetch_xp - 5, fetch_xp + 5) + addBonusXp
		new_lvl = int(((xp + xp_to_add) // 42) ** 0.55)

		db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?", xp_to_add, new_lvl, (datetime.utcnow()+timedelta(seconds=60)).isoformat(), message.author.id)
		db.commit()

		# Grant image perms
		gotImgPerm = False
		if new_lvl == 25:
			gotImgPerm = True
			await message.author.add_roles(get(self.guild.roles, name="chat perms"))

		if new_lvl > lvl:
			async with message.channel.typing():
				if gotImgPerm == True:
					await message.channel.send('Congrats {}! You reached Level {}! You now have permission to post embed links and attach files!'.format(message.author.mention, new_lvl))
				else:
					await message.channel.send('Congrats {}! You reached Level {}!'.format(message.author.mention, new_lvl))

	async def display_level(self, message, target):
		xp, lvl = db.record("SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (None, None)
		async with message.channel.typing():
			if xp:
				await message.channel.send('{} is on Level {} with {} XP.'.format(target.display_name, lvl, xp))
			else:
				await message.channel.send('This member does not have a level.')

	@command(name="level", aliases=["lvl"])
	async def say_level(self, ctx, member: Member = None):
		if member != None:
			await self.display_level(ctx, member)
		else:
			await self.display_level(ctx, ctx.author)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.ready_cogs.ready("xp")

	@Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			await self.process_xp(message, 0)


def setup(bot):
	bot.add_cog(XP(bot))