import base64
import hashlib
import json
import math
import os
import pathlib
import shutil
import time
from pathlib import Path

import discord
import requests
from apscheduler.triggers.cron import CronTrigger
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

        attributes = None
        if self.ATTR_HDR in r.headers:
            attributes = json.loads(r.headers[self.ATTR_HDR])
        user_ids = []
        if self.USER_ID_HDR in r.headers:
            user_ids = json.loads(r.headers[self.USER_ID_HDR])

        return r

    # Loads the data from a file given the datastore and key, if not found, then query to the DatastoreServices
    async def load_data(self, interaction: discord.Interaction, datastore, object_key):
        path = f"./data/temp/{datastore}/{object_key}.json"
        cachedResults = Path(path)

        if cachedResults.is_file():
            # Check if their json files was cached first
            with open(path) as f:
                return json.load(f)
        else:
            # Query the server
            data = await self.get_entry(datastore, object_key)
            status_code = data.status_code

            if status_code == 403:
                if interaction != None:
                    await interaction.response.send_message(
                        "{} The server returned 403 Unauthorized! My owner probably lost their keys again...".format(
                            interaction.user.mention
                        )
                    )
                return 403

            if status_code == 429:
                if interaction != None:
                    await interaction.response.send_message(
                        "{} The server returned error 429 Too Many Requests! Please wait a few minutes before trying again!".format(
                            interaction.user.mention
                        )
                    )
                return 429

            if status_code == 200:
                # Cache the result, and delete it after a time
                jsonResult = data.json()
                jsonResult["updated"] = time.time()

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(jsonResult, f, ensure_ascii=False, indent=4)

                return jsonResult

    # Expires individual directories
    async def expire_json(self, folder):
        files = os.listdir(folder)

        for file in files:
            if file.endswith(".json"):
                full_path = folder + "/" + file

                with open(full_path) as f:
                    data = json.load(f)
                    updated = data["updated"]

                    if (time.time() - updated) >= 300:
                        os.remove(full_path)

    # Runs expiration on all folders in temp
    async def expire_old_data(self):
        await self.expire_json("./data/temp/Account_ProfileStore_Suffix_7")
        await self.expire_json("./data/temp/Character_ProfileStore_Suffix_7")

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

                # Check if they have a Roblox ID assigned to the specified member
                id = await verification.get_roblox_id(member)

                if id:
                    accountJson = await self.load_data(
                        interaction,
                        "Account_ProfileStore_Suffix_7",
                        f"{id}_SaveData_Account",
                    )

                    characterJson = await self.load_data(
                        interaction,
                        "Character_ProfileStore_Suffix_7",
                        f"{id}_SaveData_Character_{character}",
                    )

                    if type(accountJson) == int or type(characterJson) == int:
                        return

                    if accountJson == None or characterJson == None:
                        await interaction.response.send_message(
                            "{} This character was not found in the given member!".format(
                                interaction.user.mention
                            )
                        )
                        return

                    # Determine Nemesis by seeing which enemy they got killed the most!
                    nemesis = "None"
                    mostKilledBy = 0
                    totalKills = 0
                    iterateOverEnemyTypes = ["Mobs", "Bosses"]

                    for enemyType in iterateOverEnemyTypes:
                        for enemyKey in accountJson["Data"]["Journal"][enemyType]:
                            if (
                                accountJson["Data"]["Journal"][enemyType][enemyKey][
                                    "Defeats"
                                ]
                                > mostKilledBy
                            ):
                                mostKilledBy = accountJson["Data"]["Journal"][
                                    enemyType
                                ][enemyKey]["Defeats"]
                                nemesis = enemyKey

                            totalKills += accountJson["Data"]["Journal"][enemyType][
                                enemyKey
                            ]["Kills"]

                    # Make Playcount List
                    list = ""
                    for characterName in accountJson["Data"]["CharacterPlayCount"]:
                        count = accountJson["Data"]["CharacterPlayCount"][characterName]
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
                            Bosses Defeated: {accountJson["Data"]["BossesKilled"]:,}
                            Total Kills: {totalKills:,}
                            Nemesis: {nemesis}

                            **Play Count:**
                            {list}
                            """

                    updated_difference = time.time() - characterJson["updated"]
                    updated_text = ""

                    if updated_difference <= 10:
                        updated_text = "Last updated a few seconds ago."
                    elif updated_difference <= 30:
                        updated_text = (
                            f"Last updated {round(updated_difference)} seconds ago."
                        )
                    elif updated_difference <= 60:
                        updated_text = "Last updated a minute ago."
                    elif updated_difference <= 1800:
                        updated_text = f"Last updated {round(updated_difference / 60)} minutes ago."
                    else:
                        updated_text = "Last updated a while ago."

                    embedObj = discord.Embed(
                        title=title, description=desc, colour=0x5387B8
                    )

                    imageFile = discord.File(
                        f"./img/classes/{character}.png",
                        filename=f"{character}.png",
                    )
                    embedObj.set_image(url=f"attachment://{character}.png")
                    embedObj.set_footer(text=f"{updated_text} Base stats only shown.")

                    await interaction.response.send_message(
                        file=imageFile, embed=embedObj
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
            # Delete all temporary json files
            try:
                shutil.rmtree("./data/temp")
                print("Deleted temporary directory.")
            except OSError as e:
                print(f"Error deleting temporary files: {e}")

            # Create new temporary directory
            pathlib.Path("./data/temp/Account_ProfileStore_Suffix_7").mkdir(
                parents=True, exist_ok=True
            )
            pathlib.Path("./data/temp/Character_ProfileStore_Suffix_7").mkdir(
                parents=True, exist_ok=True
            )

            self.bot.scheduler.add_job(
                self.expire_old_data,
                CronTrigger(
                    minute="1,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,59"
                ),
            )

            self.bot.ready_cogs.ready("datastore")


async def setup(bot):
    await bot.add_cog(Datastore(bot))
