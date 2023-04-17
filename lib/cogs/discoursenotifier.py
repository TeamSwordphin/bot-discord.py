import discord
import requests
from apscheduler.triggers.cron import CronTrigger
from bs4 import BeautifulSoup
from discord.ext.commands import Cog, command

TEXT_CHANNELS_TO_SEND = [410596271057797131]
LINK = "https://devforum.roblox.com/t/pwned-3-update-notes/943110/2"
LINK_JSON = f"{LINK}.json"


class Notifier(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_updated = ""

    @command(name="updatelog")
    async def post_update_log(self, ctx):
        if ctx.author.id == 105180779025334272:
            print(len(ctx.message.attachments))
            if len(ctx.message.attachments) < 1:
                print("This message does not have any attachments.")
            else:
                file_request = requests.get(ctx.message.attachments[0].url)
                response_json = file_request.json()
                await self.post_update(
                    response_json["post_stream"]["posts"][0]["updated_at"],
                    response_json,
                )

    async def post_update(self, last_updated, response_json):
        self.last_updated = last_updated

        # Parse the HTML, making it a readable format
        soup = BeautifulSoup(
            response_json["post_stream"]["posts"][0]["cooked"], features="html.parser"
        )
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

        embedObj = discord.Embed(title=title, description=desc, colour=0x5387B8)
        embedObj.set_image(url="https://i.imgur.com/mRGGwre.png")
        embedObj.set_footer(text="These patch notes may be subject to change.")

        for channel_id in TEXT_CHANNELS_TO_SEND:
            channel = await self.bot.fetch_channel(channel_id)
            if channel:
                await channel.send(embed=embedObj)

    async def get_last_update(self):
        response = requests.get(LINK_JSON)
        if response.status_code != 403:
            response_json = response.json()
            return response_json["post_stream"]["posts"][0]["updated_at"], response_json
        else:
            #    print("Response returned 403.")
            return None, None

    async def check_post(self):
        last_updated, response_json = await self.get_last_update()

        if last_updated != None:
            if self.last_updated != last_updated:
                await self.post_update()

    @command(name="getPost")
    async def say_discourse_post(self, ctx):
        last_update, _ = await self.get_last_update()
        await ctx.send(f"Team Swordphin Update Logs was last updated at {last_update}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            last_updated, _ = await self.get_last_update()
            if last_updated != None:
                self.last_updated = last_updated

            # self.bot.scheduler.add_job(
            #    self.check_post,
            #    CronTrigger(
            #        minute="3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,59"
            #    ),
            # )

            self.bot.ready_cogs.ready("discoursenotifier")


async def setup(bot):
    await bot.add_cog(Notifier(bot))
