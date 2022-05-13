from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import sleep
from glob import glob
from ..db import db

import discord
from discord import Intents, Embed
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import CommandNotFound

PREFIX = "!"
OWNER_IDS = [105180779025334272]
GUILD = 311200318895423499
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class CogsReady(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready(self, cog):
		setattr(self, cog, True)
		print(f"{cog} cog ready")

	def ready_all(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.ready_cogs = CogsReady()
		self.prefix = PREFIX
		self.guild = None
		self.scheduler = AsyncIOScheduler()
		
		db.autosave(self.scheduler)
		super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=Intents.all())

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f"{cog} cog loaded")
		
	def run(self, version):
		self.version = version
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tokenFile:
			self.token = tokenFile.read()

		super().run(self.token, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)

		if ctx.command is not None and ctx.guild is not None:
			if self.ready:
				await self.invoke(ctx)
			else:
				await ctx.send("Bot not ready to receive commands!")

	async def on_connect(self):
		print("Bot connected!")

	async def on_disconnect(self):
		print("Bot disconnected!")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong!")
		raise

	async def on_command_error(self, ctx, exc):
		if isinstance(exc, CommandNotFound):
			pass
		else:
			raise exc

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(GUILD)
			self.scheduler.start()

			await self.change_presence(status=discord.Status.dnd, activity=discord.Game("with Sword!"))

			while not self.ready_cogs.ready_all():
				await sleep(0.5)

			self.ready = True
			print("bot ready")
		else:
			print("bot reconnected")
		
	async def on_message(self, message):
		if not message.author.bot:
			await self.process_commands(message)


bot = Bot()