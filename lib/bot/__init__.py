from asyncio import sleep
from glob import glob

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, Context

from ..db import db

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
        super().__init__(
            command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=Intents.all()
        )

    def run(self, version):
        self.version = version

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

    async def setup_hook(self):
        for cog in COGS:
            print(f"{cog} Loading...")
            await self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} Loaded!")

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(GUILD)
            self.scheduler.start()

            await self.change_presence(
                status=discord.Status.dnd, activity=discord.Game("with Sword!")
            )

            print("Readying cogs...")

            while not self.ready_cogs.ready_all():
                await sleep(0.5)

            print("Cogs are all ready!")

            try:
                synced = await self.tree.sync()
                print(f"Synced {len(synced)} commands!")
            except Exception as e:
                print(e)

            self.ready = True
            print("bot ready")
        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
