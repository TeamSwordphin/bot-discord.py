import base64
import hashlib
import json
import math
from typing import Optional

import discord
import requests
from discord import Member, app_commands
from discord.ext.commands import Cog


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

    @app_commands.command(
        name="character",
        description="Find the character save of a user from PWNED 3 and display it in chat.",
    )
    @app_commands.describe(
        member="Choose a member! If left out, defaults to yourself.",
        character="Choose a P3 character! Defaults to Darwin.",
    )
    @app_commands.choices(
        character=[
            app_commands.Choice(name="Darwin", value="DarwinB"),
            app_commands.Choice(name="Valeri", value="Valeri"),
            app_commands.Choice(name="Red", value="Red"),
            app_commands.Choice(name="Clyde", value="Clyde"),
            app_commands.Choice(name="LingeringForce", value="LingeringForce"),
            app_commands.Choice(name="Natsuko", value="Natsuko"),
            app_commands.Choice(name="Alburn", value="Alburn"),
            app_commands.Choice(name="Stella", value="Stella"),
        ]
    )
    async def show_character_profile(
        self,
        interaction: discord.Interaction,
        member: Member,
        character: app_commands.Choice[str],
    ) -> None:
        character = character.value

        if character == "Darwin":
            character = "DarwinB"

        xpSystem = self.bot.get_cog("XP")
        verification = self.bot.get_cog("Verification")

        _, lvl = await xpSystem.get_stats(interaction.user)

        async with interaction.channel.typing():
            if lvl < 75:
                await interaction.response.send_message(
                    "{} You must be at least Level 75 in the Discord Server before you can use this command!".format(
                        interaction.user.mention
                    )
                )
            else:
                if member is None:
                    member = interaction.user

                id = await verification.get_roblox_id(member)

                if id:
                    accountData = await self.get_entry(
                        "Account_ProfileStore_Suffix_7",
                        "{}_SaveData_Account".format(id),
                    )

                    characterData = await self.get_entry(
                        "Character_ProfileStore_Suffix_7",
                        "{}_SaveData_Character_{}".format(id, character),
                    )

                    ac_status = accountData.status_code
                    ch_status = accountData.status_code

                    if ac_status == 403 or ch_status == 403:
                        await interaction.response.send_message(
                            "{} The server returned 403 Unauthorized! My owner probably lost their keys again...".format(
                                interaction.user.mention
                            )
                        )
                        return

                    if ac_status == 429 or ch_status == 429:
                        await interaction.response.send_message(
                            "{} The server returned error 429 Too Many Requests! Please wait a few minutes before trying again!".format(
                                interaction.user.mention
                            )
                        )
                        return

                    if ac_status == 200 and ch_status == 200:
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

                        # Make Playcount List
                        list = ""
                        for characterName in accountJson["Data"]["CharacterPlayCount"]:
                            count = accountJson["Data"]["CharacterPlayCount"][
                                characterName
                            ]
                            list = list + f"• {characterName} - {count:,}\n"

                        title = f"Account Information for {member.name}"
                        desc = f"""**Featured Character:** {character}
                                Level: {characterJson["Data"]["CurrentLevel"]}
                                HP: {characterJson["Data"]["HP"]:,}
                                Damage: {characterJson["Data"]["Damage"]:,}
                                Defense: {math.floor((characterJson["Data"]["Defense"] * 100) + 0.5)}%
                                Stamina: {characterJson["Data"]["Stamina"]:,}
                                Critical: {characterJson["Data"]["Crit"]:,}
                                Sturdiness: {characterJson["Data"]["CritDef"]:,}
                                Mastery Level: {characterJson["Data"]["MasteryLevel"]}

                                **Fun Stats:**
                                Hours Played: {math.floor((accountJson["Data"]["TotalHours"] / 3600) + 0.5):,}
                                Highest Combo: {accountJson["Data"]["HighestCombo"]:,}
                                Highest Damage: {accountJson["Data"]["HighestDamage"]:,}
                                Bosses Killed: {accountJson["Data"]["BossesKilled"]:,}
                                Nemesis: {nemesis}

                                **Play Count:**
                                {list}
                                """

                        embedObj = discord.Embed(
                            title=title, description=desc, colour=0x5387B8
                        )

                        imageFile = discord.File(
                            f"./img/classes/{character}.png",
                            filename=f"{character}.png",
                        )
                        embedObj.set_image(url=f"attachment://{character}.png")
                        embedObj.set_footer(
                            text="These changes do not update live. Base stats only shown."
                        )

                        await interaction.response.send_message(
                            file=imageFile, embed=embedObj
                        )
                    else:
                        await interaction.response.send_message(
                            "{} Character does not exist. Please make sure you have typed the right character name (case sensitive!) and try again in a minute.".format(
                                interaction.user.mention
                            )
                        )
                else:
                    await interaction.response.send_message(
                        "{} You do not have a Roblox profile set! Please re-verify before using this command.".format(
                            interaction.user.mention
                        )
                    )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready_cogs.ready("datastore")


async def setup(bot):
    await bot.add_cog(Datastore(bot))
