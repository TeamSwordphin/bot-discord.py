from typing import Optional
from ..db import db

import discord
from discord import Member
from discord.ext.commands import Cog, command
from discord.utils import get

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
		db.multiexecute("DELETE FROM warnlog WHERE UserID = ?", ((id_,) for id_ in to_remove))
		db.commit()

	@command(name="strike", aliases=["warn"])
	async def record_warning(self, ctx, member: Member = None, *, warning: Optional[str] = "No warning was given."):
		if member != None:
			roleMod = get(self.bot.guild.roles, name="Moderator") # Get the role
			roleSup = get(self.bot.guild.roles, name="Support Developers")

			if roleMod in ctx.author.roles or roleSup in ctx.author.roles:
				db.execute("INSERT INTO warnlog (UserID, Reason) VALUES (?, ?)", member.id, warning)
				db.commit()
				title = f"{member.name} has been given a strike!"
				desc = warning
				await ctx.send(embed=discord.Embed(title=title, description=desc, colour=0x5387b8))
				await ctx.message.delete()

	@command(name="strikes", aliases=["warnings", "warns", "getwarns", "getwarnings", "getstrikes"])
	async def get_warnings(self, ctx, member: Member = None):
		if member != None:
			roleMod = get(self.bot.guild.roles, name="Moderator") # Get the role
			roleSup = get(self.bot.guild.roles, name="Support Developers")

			if roleMod in ctx.author.roles or roleSup in ctx.author.roles:
				reasons = db.records("SELECT Reason FROM warnlog WHERE UserID = ?", member.id)
				strikeNo = 1
				for reason in reasons:
					title = f"Strike {str(strikeNo)}"
					desc = ''.join(reason)
					strikeNo += 1
					await ctx.send(embed=discord.Embed(title=title, description=desc, colour=0x5387b8))

	@command(name="resetstrikes", aliases=["resetstrike"])
	async def reset_strikes(self, ctx, member: Member = None):
		if member != None:
			roleMod = get(self.bot.guild.roles, name="Moderator") # Get the role
			roleSup = get(self.bot.guild.roles, name="Support Developers")

			if roleMod in ctx.author.roles or roleSup in ctx.author.roles:
				db.execute("DELETE FROM warnlog WHERE UserID = ?", member.id)
				await ctx.send(f'{member.mention} strikes has been reset.')

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			await self.update_db()
			self.bot.ready_cogs.ready("warnsystem")

	# Delete to databases
	@Cog.listener()
	async def on_member_remove(self, member):
		db.execute("DELETE FROM warnlog WHERE UserID = ?", member.id)


def setup(bot):
	bot.add_cog(Warn(bot))