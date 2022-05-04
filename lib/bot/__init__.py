from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase

PREFIX = "!"
OWNER_IDS = [105180779025334272]
GUILD = 334163198976589837


class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.prefix = PREFIX
		self.guild = None
		self.scheduler = AsyncIOScheduler()
		
		super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)
		
	def run(self, version):
		self.version = version

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tokenFile:
			self.token = tokenFile.read()

		print("running bot")
		super().run(self.token, reconnect=True)

	async def on_connect(self):
		print("Bot connected!")

	async def on_disconnect(self):
		print("Bot disconnected!")

	async def on_ready(self):
		if not self.ready:
			self.ready = True
			self.guild = self.get_guild(GUILD)
			print("bot ready")
		else:
			print("bot reconnected")
		
	async def on_message(self, message):
		pass


bot = Bot()