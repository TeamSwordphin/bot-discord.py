from discord.ext.commands import Cog, command
from typing import Optional
from discord import Member

import discord
import hashlib
import requests
import json
import base64
import math


class Datastore(Cog):
    def __init__(self, bot):
        self.bot = bot
        self._base_url = "https://apis.roblox.com/datastores/v1/universes/"

        with open(
            "./lib/bot/robloxOpenCloudToken.0", "r", encoding="utf-8"
        ) as tokenFile:
            self._apiKey = tokenFile.read()

        self._universeId = "222994363"
        self.ATTR_HDR = "Roblox-entry-Attributes"
        self.USER_ID_HDR = "Roblox-entry-UserIds"
        self._objects_url = (
            self._base_url
            + self._universeId
            + "/standard-datastores/datastore/entries/entry"
        )
        self._increment_url = self._objects_url + "/increment"
        self._version_url = self._objects_url + "/versions/version"
        self._list_objects_url = (
            self._base_url + self._universeId + "/standard-datastores/datastore/entries"
        )

    def _H(self):
        return {"x-api-key": self._apiKey}

    def _get_url(self, path_format: str):
        return f"{self._config['base_url']}/{path_format.format(self._config['universe_id'])}"

    async def get_entry(self, datastore, object_key, scope=None):
        self._objects_url = (
            self._base_url
            + self._universeId
            + "/standard-datastores/datastore/entries/entry"
        )

        headers = {"x-api-key": self._apiKey}
        params = {"datastoreName": datastore, "entryKey": object_key}
        if scope:
            params["scope"] = scope
        r = requests.get(self._objects_url, headers=headers, params=params)
        if "Content-MD5" in r.headers:
            expected_checksum = r.headers["Content-MD5"]
            checksum = base64.b64encode(hashlib.md5(r.content).digest())
            # print(f'Expected {expected_checksum},  got {checksum}')

        attributes = None
        if self.ATTR_HDR in r.headers:
            attributes = json.loads(r.headers[self.ATTR_HDR])
        user_ids = []
        if self.USER_ID_HDR in r.headers:
            user_ids = json.loads(r.headers[self.USER_ID_HDR])

        return r

    @command(name="character", aliases=["showcharacter"])
    async def show_character_profile(
        self, ctx, member: Member = None, character: Optional[str] = "DarwinB"
    ):
        if character == "Darwin":
            character = "DarwinB"

        xpSystem = self.bot.get_cog("XP")
        verification = self.bot.get_cog("Verification")

        _, lvl = await xpSystem.get_stats(ctx.author)

        async with ctx.channel.typing():
            if lvl < 75:
                await ctx.channel.send(
                    "{} You must be at least Level 75 in the Discord Server before you can use this command!".format(
                        ctx.author.mention
                    )
                )
            else:
                user = None

                if member != None:
                    user = member
                else:
                    user = ctx.author

                id = await verification.get_roblox_id(user)

                if id:
                    accountData = await self.get_entry(
                        "Account_ProfileStore_Suffix_7",
                        "{}_SaveData_Account".format(id),
                    )

                    characterData = await self.get_entry(
                        "Character_ProfileStore_Suffix_7",
                        "{}_SaveData_Character_{}".format(id, character),
                    )

                    if (
                        accountData.status_code < 400
                        and characterData.status_code < 400
                    ):
                        accountJson = accountData.json()
                        characterJson = characterData.json()

                        # Determine Nemesis by seeing which enemy they got killed the most!
                        nemesis = "None"
                        kills = 0
                        iterateOverEnemyTypes = ["Mobs", "Bosses"]

                        for enemyType in iterateOverEnemyTypes:
                            for enemyKey in accountJson["Data"]["Journal"][enemyType]:
                                if (
                                    accountJson["Data"]["Journal"][enemyType][enemyKey][
                                        "Defeats"
                                    ]
                                    > kills
                                ):
                                    kills = accountJson["Data"]["Journal"][enemyType][
                                        enemyKey
                                    ]["Defeats"]
                                    nemesis = enemyKey

                        title = f"Account Information for {user.name}"
                        desc = f"""**Featured Character:** {character}
                                Level: {characterJson["Data"]["CurrentLevel"]}
                                HP: {characterJson["Data"]["HP"]:,}
                                Damage: {characterJson["Data"]["Damage"]:,}
                                Stamina: {characterJson["Data"]["Stamina"]:,}
                                Critical: {characterJson["Data"]["Crit"]:,}
                                Sturdiness: {characterJson["Data"]["CritDef"]:,}

                                **Fun Stats:**
                                Hours Played: {math.floor((accountJson["Data"]["TotalHours"] / 3600) + 0.5):,}
                                Highest Combo: {accountJson["Data"]["HighestCombo"]:,}
                                Highest Damage: {accountJson["Data"]["HighestDamage"]:,}
                                Bosses Killed: {accountJson["Data"]["BossesKilled"]:,}
                                Nemesis: {nemesis}
                                """

                        embedObj = discord.Embed(
                            title=title, description=desc, colour=0x5387B8
                        )

                        imageFile = discord.File(
                            f"./img/classes/{character}.png",
                            filename=f"{character}.png",
                        )
                        embedObj.set_image(url=f"attachment://{character}.png")
                        embedObj.set_footer(text="These changes do not update live.")

                        await ctx.channel.send(file=imageFile, embed=embedObj)
                    else:
                        await ctx.channel.send(
                            "{} Reached the quota limit or character does not exist. Please make sure you have typed the right character name (case sensitive!) and try again in a minute.".format(
                                ctx.author.mention
                            )
                        )
                else:
                    await ctx.channel.send(
                        "{} You do not have a Roblox profile set! Please re-verify before using this command.".format(
                            ctx.author.mention
                        )
                    )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("datastore")


def setup(bot):
    bot.add_cog(Datastore(bot))
