import json
import uuid

import discord
import requests
from discord import app_commands
from discord.ext.commands import Cog


class MessagingService(Cog):
    def __init__(self, bot):
        self.bot = bot
        self._base_url = "https://apis.roblox.com/messaging-service/v1/universes/"

        with open(
            "./lib/bot/robloxOpenCloudToken.0", "r", encoding="utf-8"
        ) as tokenFile:
            self._apiKey = tokenFile.read()

        self._universeId = "222994363"
        self._topic = "ShopInterfaceUpdater"
        self._objects_url = self._base_url + self._universeId + "/topics/" + self._topic

    @app_commands.command(
        name="shopkeep", description="Enable or disable certain shop items in P3."
    )
    @app_commands.describe(
        category="The category this item is in.",
        tab="The tab this item is located.",
        item="The item in question. Case sensitive.",
        purchasable="Enable or disable the ability to purchase this item for users.",
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name="Account", value="Account"),
            app_commands.Choice(name="Black Market", value="Black Market"),
            app_commands.Choice(name="Cosmetics", value="Cosmetics"),
            app_commands.Choice(name="Custom Order", value="Custom Order"),
            app_commands.Choice(name="Persona", value="Persona"),
            app_commands.Choice(name="Rewards", value="Rewards"),
        ],
        tab=[
            app_commands.Choice(name="Consumables", value="Consumables"),
            app_commands.Choice(name="Upgrades", value="Upgrades"),
            app_commands.Choice(name="Game Passes", value="Game Passes"),
            app_commands.Choice(name="Tears", value="Tears"),
            app_commands.Choice(name="Aura Boxes", value="Aura Boxes"),
            app_commands.Choice(name="Banners", value="Banners"),
            app_commands.Choice(name="Costumes", value="Costumes"),
            app_commands.Choice(name="Emojis", value="Emojis"),
            app_commands.Choice(name="Pets", value="Pets"),
            app_commands.Choice(name="Player Cards", value="Player Cards"),
            app_commands.Choice(name="Account", value="Account"),
            app_commands.Choice(name="Gemstones", value="Gemstones"),
            app_commands.Choice(name="Characters", value="Characters"),
            app_commands.Choice(name="Evocations", value="Evocations"),
        ],
        purchasable=[
            app_commands.Choice(name="On", value="False"),
            app_commands.Choice(name="Off", value="True"),
        ],
    )
    async def shopkeep(
        self,
        interaction: discord.Interaction,
        category: app_commands.Choice[str],
        tab: app_commands.Choice[str],
        item: str,
        purchasable: app_commands.Choice[str],
    ) -> None:
        if item == None:
            await interaction.response.send_message(
                f"{interaction.user.mention} Item must not be nothing!"
            )
            return

        headers = {"x-api-key": self._apiKey, "Content-Type": "application/json"}
        data = {
            "Category": category.value,
            "Tab": tab.value,
            "Item": item,
            "Enabled": purchasable.value,
        }

        response = requests.post(
            self._objects_url, json={"message": json.dumps(data)}, headers=headers
        )

        if response.status_code == 400:
            await interaction.response.send_message(
                "Roblox returned Status Code 400. Is there a server running?"
            )
        elif response.status_code == 500:
            await interaction.response.send_message(
                "Roblox returned Status Code 500, internal server error. Maybe Roblox is down?"
            )
        elif response.status_code == 200:
            await interaction.response.send_message(
                "Request successfully sent! If you don't see a message in the game's chat, you may have spelled 'Item' wrong!"
            )
        else:
            await interaction.response.send_message(f"{str(response)}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("messagingservice")


async def setup(bot):
    await bot.add_cog(MessagingService(bot))
