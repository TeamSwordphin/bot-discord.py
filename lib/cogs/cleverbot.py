import cleverbot
import random
from random import randint

from discord.ext.commands import Cog, command


REACTIONS = [
	':TSPwhenlifegetsatred:597270319736291347',
	':TSPvaleriSmug:585958568822571011',
	':TSPvaleriShrug:613461305025626132',
	':TSPvaleriPog:613439446800531463', 
	':TSPshopkeepEZ:586372671646728193', 
	':TSPredREEgif:597273299449544705',
	':TSPredAYAYA:585953483744608256',
	':TSPphinYes:590373864194965505',
	':TSPphinNo:590371307850432517',
	':TSPnatsukoWowgif:612058636986089526',
	':TSPnatsukoCry:586327903340331068',
	':TSPlilahLewd:585661944367808522',
	':TSPdarwinWeird:613457203491242024', 
	':TSPdarwinS:613460365732347911',
	':TSPalburnPinged:586724160244285440'
]

class Cleverbot(Cog):
	def __init__(self, bot):
		self.bot = bot

		with open("./lib/bot/cleverbot.0", "r", encoding="utf-8") as tokenFile:
			self.conversation = cleverbot.Cleverbot(tokenFile.read(), timeout=60)
			self.conversation.reset()

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.ready_cogs.ready("cleverbot")

	@Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			if self.bot.user in message.mentions:
				command = message.content.split()
				if len(command) > 1:
					async with message.channel.typing():
						command.pop(0)
						newStr = ' '.join(command)
						try:
							reply = self.conversation.say(newStr)
						except cleverbot.CleverbotError as error:
							await message.channel.send(error)
						else:
							await message.channel.send(reply)
						finally:
							self.conversation.close()
				else:
					randomReaction = random.choice(REACTIONS)
					await message.add_reaction(randomReaction)

def setup(bot):
	bot.add_cog(Cleverbot(bot))