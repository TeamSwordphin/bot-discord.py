import os
import random
import time

import cleverbot
import discord
from discord.ext.commands import Cog

REACTIONS = [
    597270319736291347,
    585958568822571011,
    613461305025626132,
    613439446800531463,
    586372671646728193,
    597273299449544705,
    585953483744608256,
    590373864194965505,
    590371307850432517,
    612058636986089526,
    586327903340331068,
    585661944367808522,
    613457203491242024,
    613460365732347911,
    586724160244285440,
]


class Cleverbot(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_time_since_video_was_sent = 0

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

                        newStr = " ".join(command)

                        try:
                            reply = self.conversation.say(newStr)
                        except cleverbot.CleverbotError as error:
                            await message.channel.send(error)
                        else:
                            await message.channel.send(reply)
                        finally:
                            self.conversation.close()
                else:
                    # Reply with a random emoji!
                    randomReaction = random.choice(REACTIONS)
                    emoji = self.bot.get_emoji(randomReaction)

                    if emoji:
                        await message.add_reaction(emoji)

                    # Then send a video!
                    current_time = time.time()

                    if (current_time - self.last_time_since_video_was_sent) >= 600:
                        self.last_time_since_video_was_sent = current_time

                        base_dir = "./video"
                        video_path_random = random.choice(
                            [
                                x
                                for x in os.listdir(base_dir)
                                if os.path.isfile(os.path.join(base_dir, x))
                            ]
                        )

                        if video_path_random:
                            await message.reply(
                                file=discord.File(
                                    os.path.join(base_dir, video_path_random)
                                )
                            )


async def setup(bot):
    await bot.add_cog(Cleverbot(bot))
