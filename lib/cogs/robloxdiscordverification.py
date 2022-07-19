from ast import alias
import requests
from ..db import db

import discord
from discord import Member
from discord.utils import get
from discord.ext.commands import Cog, command

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
		db.multiexecute("INSERT OR IGNORE INTO robloxverification (UserID) VALUES (?)",
			((member.id,) for member in self.bot.guild.members if not member.bot)
		)

		# Remove verification from left members
		to_remove = []
		stored_members = db.column("SELECT UserID FROM robloxverification")
		for id_ in stored_members:
			if not self.bot.guild.get_member(id_):
				to_remove.append(id_)
		db.multiexecute("DELETE FROM robloxverification WHERE UserID = ?", ((id_,) for id_ in to_remove))
		db.commit()

	@command(name="verifyme")
	async def say_verification(self, ctx, userid: str = None):
		if can_send_in_channel(ctx.channel.id):
			if userid != None:
				json = await self.get_json(f"https://users.roblox.com/v1/users/{userid}")
				if json.get("id"):
					strCount = json["description"].find("!verifyme")
					if strCount != -1:
						# Check if they are in the group
						groupJson = await self.get_json(f"https://groups.roblox.com/v1/users/{userid}/groups/roles")
						inGroup = False

						for groupInfo in groupJson["data"]:
							group = groupInfo.get("group")
							if group:
								groupId = group.get("id")
								if groupId:
									if groupId == SWORD_FISH_CLUB_ID:
										inGroup = True

						db.execute("UPDATE robloxverification SET RobloxProfileLink = ? WHERE UserID = ?", userid, ctx.author.id)
						db.commit()

						if inGroup:
							await ctx.author.add_roles(get(self.bot.guild.roles, name="Swordfish Club"))
							print("GAVE SWORDFISH ROLE!!")
						else:
							await ctx.author.add_roles(get(self.bot.guild.roles, name="Not in the club"))
							print("NOT IN THE CLUB ROLE!!")

						bot_channel = await self.bot.fetch_channel(410596271057797131)
						await ctx.author.edit(nick=json.get("name"))
						await bot_channel.send(f"{ctx.author.mention} was verified from Roblox User ID {userid}")

					else:
						await ctx.send(f"Found your Roblox Profile {ctx.author.mention}! Please follow the instructions below to continue verification:")
						description = """**Step 1**
						Please go to your Roblox Profile, edit your User Profile's description to include the tag "!verifyme".

						**Step 2**
						Come back here, and type in "!verifyme YOUR_USER_ID_HERE" again.

						**Step 3**
						You may remove this tag once verification is complete.
						"""

						embedObj = discord.Embed(title = "Verification Pt.2", description = description, colour = 0x5387b8)
						await ctx.send(embed=embedObj)
						await ctx.send("https://i.imgur.com/Aa57Gr8.mp4")
						
				else:
					await ctx.send(f"Hi {ctx.author.mention}, I did not find a user that goes under the id of **{userid}**! Please make sure the id you gave is correct.")
			else:
				await ctx.send(f"Please follow the instructions below to verify yourself:")
				description = """Please use the command !verifyme followed by the UserId of your Roblox Profile. For example:

				**!verifyme YOUR_USER_ID_HERE**
				**!verifyme 297701**

				To find your UserId, please go to your Roblox profile, and copy the numbers from the URL bar:
				"""

				embedObj = discord.Embed(title = "Verification Instructions", description = description, colour = 0x5387b8)
				embedObj.set_image(url="https://i.imgur.com/81H6jxP.png")
				await ctx.send(embed=embedObj)

	@command(name="setprofile")
	async def set_roblox_profile(self, ctx, member: Member = None, userid: str = None):
		if member != None:
			roleMod = get(self.bot.guild.roles, name="Moderator") # Get the role
			roleSup = get(self.bot.guild.roles, name="Support Developers")

			if roleMod in ctx.author.roles or roleSup in ctx.author.roles:
				json = await self.get_json(f"https://users.roblox.com/v1/users/{userid}")
				if json.get("id"):
					db.execute("UPDATE robloxverification SET RobloxProfileLink = ? WHERE UserID = ?", userid, member.id)
					db.commit()
					name = json.get("name")
					await ctx.send(f"{member.mention} profile set to {name}. Remember to manually set their nickname if applicable.")
				else:
					await ctx.send(f"Could not find Roblox Profile with userid {userid}")
		else:
			await ctx.send("You must also specify a member.")

	@command(name="verifyprofile", aliases=["viewprofile", "profile"])
	async def verify_roblox_profile(self, ctx, member: Member = None):
		link = None
		if member != None:
			link = db.record("SELECT RobloxProfileLink FROM robloxverification WHERE UserID = ?", member.id)
		else:
			link = db.record("SELECT RobloxProfileLink FROM robloxverification WHERE UserID = ?", ctx.author.id)
			
		if link != None:
			id = ''.join(link)
			await ctx.send(f"https://www.roblox.com/users/{id}/profile")
		else:
			await ctx.send("This user's Roblox Profile was not found.")

	@command(name = "gettesters", pass_context=True)  
	async def getuser(self, ctx):
		roleSup = get(self.bot.guild.roles, name="Support Developers")
		if roleSup in ctx.author.roles:
			empty = True
			roleTester = get(self.bot.guild.roles, name="Cubicle Office Worker")

			# Get all objects, and combine them into a bulletpointed list
			list = ""
			for member in self.bot.guild.members:
				if roleTester in member.roles:
					link = db.record("SELECT RobloxProfileLink FROM robloxverification WHERE UserID = ?", member.id)
					id = ''.join(link)
					json = await self.get_json(f"https://users.roblox.com/v1/users/{id}")
					if json.get("id"):
						name = json.get("name")
						list = list + f"• {member.mention} is set to [{name}] with UserId **{id}**.\n"
						empty = False
					else:
						list = list + f"• {member.name} does not have a UserId set.\n"

			if empty:
				await ctx.send(f"Nobody has the role {roleTester.name}")
			else:
				await ctx.send(embed=discord.Embed(title="Tester Roblox Profiles", description=list, colour=0x5387b8))

	# Ping the user for verification instructions
	@Cog.listener()
	async def on_member_join(self, member):
		db.execute("INSERT INTO robloxverification (UserID) VALUES (?)", member.id)
		verification_channel = await self.bot.fetch_channel(734172216299880480)
		await verification_channel.send(f"{member.mention} Welcome to the Official Team Swordphin Discord!")
		description = """Please follow the exact instructions below to verify yourself:

		**Normal Verification**
		Please type !verifyme

		*This method of verification gives you the exclusive Swordfish Club role if you are in the Roblox group*
		"""

		embedObj = discord.Embed(title = "How to Verify Yourself", description = description, colour = 0x5387b8)
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

def setup(bot):
	bot.add_cog(Verification(bot))