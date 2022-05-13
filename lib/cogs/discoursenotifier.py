import requests
from bs4 import BeautifulSoup
from apscheduler.triggers.cron import CronTrigger

import discord
from discord.ext.commands import Cog, command


TEXT_CHANNELS_TO_SEND = [410596428348391445, 410995977688842240]
LINK = "https://devforum.roblox.com/t/pwned-3-update-notes/943110/1"
LINK_JSON = f"{LINK}.json"

class Notifier(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.last_updated = ""

	async def get_last_update(self):
		response = requests.get(LINK_JSON)
		response_json = response.json()
		return response_json["post_stream"]["posts"][0]["updated_at"], response_json

	async def check_post(self):
		last_updated, response_json = await self.get_last_update()
		if self.last_updated != last_updated:
			self.last_updated = last_updated

			# Parse the HTML, making it a readable format
			soup = BeautifulSoup(response_json["post_stream"]["posts"][0]["cooked"], features="html.parser")
			divs = soup.findAll("li")

			# Get all objects, and combine them into a bulletpointed list
			list = ""
			for children in divs:
				list = list + f"• {children.string}\n"

			# Create embed object
			title = f"{response_json['title']}"
			desc = f"""<Last updated on {last_updated}>

					**Summary of changes**
					{list}
					**To see the full changelog, please use the link below**
					{LINK}
					"""

			embedObj = discord.Embed(title=title, description=desc, colour=0x5387b8)
			embedObj.set_image(url="https://i.imgur.com/mRGGwre.png")
			embedObj.set_footer(text="These patch notes may be subject to change.")
			
			for channel_id in TEXT_CHANNELS_TO_SEND:
				channel = await self.bot.fetch_channel(channel_id)
				if channel:
					await channel.send(embed=embedObj)

	@command(name="getPost")
	async def say_discourse_post(self, ctx):
		last_update, _ = await self.get_last_update()
		await ctx.send(f"Team Swordphin Update Logs was last updated at {last_update}")

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			last_updated, _ = await self.get_last_update()
			self.last_updated = last_updated
			self.bot.scheduler.add_job(self.check_post, CronTrigger(second="0,20,40"))
			self.bot.ready_cogs.ready("discoursenotifier")

def setup(bot):
	bot.add_cog(Notifier(bot))