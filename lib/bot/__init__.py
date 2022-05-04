from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents, Embed
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from glob import glob
from ..db import db

PREFIX = "!"
OWNER_IDS = [105180779025334272]
GUILD = 334163198976589837
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.prefix = PREFIX
		self.guild = None
		self.scheduler = AsyncIOScheduler()
		
		db.autosave(self.scheduler)
		super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=Intents.all())

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f"{cog} cog loaded")

		print("setup complete")
		
	def run(self, version):
		self.version = version
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tokenFile:
			self.token = tokenFile.read()

		print("running bot")
		super().run(self.token, reconnect=True)

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
			raise exc.original

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(GUILD)
			self.scheduler.start()
			self.ready = True
			print("bot ready")
		else:
			print("bot reconnected")
		
	async def on_message(self, message):
		pass


bot = Bot()