import discord
from discord.ext.commands import Cog, command
from quart import Quart, request

app = Quart(__name__)

# Bot messages are enabled here
@app.route("/", methods=["POST"])
async def index():
    data = await request.get_json()

    if data:
        # Get the message
        topic = data.get("topic", "")
        message = data.get("message", "")

        if topic and message:
            channel = await app.bot.fetch_channel(919686018762956820)
            if channel:
                await channel.send(
                    embed=discord.Embed(
                        title=topic, description=message, colour=0x5387B8
                    )
                )

            return "2"
        else:
            return "1"
    else:
        return "0"


class SaveEditor(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            app.bot = self.bot
            self.bot.loop.create_task(app.run_task(host="0.0.0.0", port=5000))
            self.bot.ready_cogs.ready("saveeditornotifier")


async def setup(bot):
    await bot.add_cog(SaveEditor(bot))
