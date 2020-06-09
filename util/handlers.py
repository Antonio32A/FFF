import json
from datetime import datetime

import asyncio
import gspread_asyncio
from oauth2client.service_account import ServiceAccountCredentials


class Handlers:
    """
    A collection of multiple handlers
    """
    class JSON:
        """
        Simple JSON handler for reading and dumping JSON data into files
        """
        @staticmethod
        def read(file):
            """
            Reads files and returns their JSON data
            :param (str) file: The file to read
            :returns (dict) data: JSON data of the file
            """
            with open(f"{file}.json", "r", encoding="utf8") as file:
                data = json.load(file)
            return data

        @staticmethod
        def dump(file, data):
            """
            Dumps JSON data into a file
            :param (str) file: The file to dump data to
            :param (dict) data: The JSON data to dump into the file
            """
            with open(f"{file}.json", "w", encoding="utf8") as file:
                json.dump(data, file, indent=4)

    class Mojang:
        """
        An API handler for Mojang's API
        """
        def __init__(self, session):
            self.mojang_url = "https://api.mojang.com/"
            self.session = session

        async def get_player_uuid(self, username: str):
            """
            Gets the Minecraft UUID of the player
            :param (str) username: The player's username
            :returns (str) uuid: The player's Minecraft UUID
            """
            async with self.session.get(f"{self.mojang_url}users/profiles/minecraft/{username}") as data:
                data = await data.text()
            return json.loads(data)['id']

        async def get_player_username(self, uuid: str):
            """
            Gets the Minecraft username of the player
            :param (str) uuid: The player's Minecraft UUID
            :returns (str) username: The player's username
            """
            async with self.session.get(f"{self.mojang_url}user/profiles/{uuid}/names") as data:
                data = await data.text()
            return json.loads(data)[-1]['name']

    class Spreadsheet:
        """
        An API handler for Google Spreadsheets
        """
        def __init__(self, key):
            self.key = key
            self.client_manager = gspread_asyncio.AsyncioGspreadClientManager(self.get_credentials)
            self.worksheet = None

        @staticmethod
        def get_credentials():
            """
            Gets the credentials because it is required for the AsyncioGspreadClientManager
            :returns (ServiceAccountCredentials): The credentials
            """
            return ServiceAccountCredentials.from_json_keyfile_name(
                "google_service_account_secret.json",
                [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/spreadsheets",
                ],
            )

        async def auth(self):
            """
            Authenticates the AsyncioGspreadClientManager for Google Spreadsheets
            """
            agc = await self.client_manager.authorize()
            spreadsheet = await agc.open_by_key(self.key)
            self.worksheet = spreadsheet.sheet1

        def get_all_users(self):
            """
            Gets all users in the Google Spreadsheets worksheet and gets their 'paid' and 'paid_to' data
            :returns (dict) users: The dict with all the users and their 'paid' and 'paid_to' data
            """
            users = {}
            records = self.worksheet.get_all_records()
            for record in records:
                paid = record['paid']
                if paid == "TRUE":
                    paid = True
                else:
                    paid = False

                users[record['uuid']] = {
                    "paid": paid,
                    "paid_to": record['paid_to']
                }
            return users

        def clear(self):
            """
            Clears the worksheet
            """
            self.worksheet.clear()

        def append_row(self, row: list):
            """
            Appends a row to the worksheet
            :param (list) row: The row to append
            """
            self.worksheet.append_row(row)

        def insert_rows(self, rows: list, index: int = 1):
            """
            Inserts multiple rows in the worksheet
            :param (list) rows: The rows to insert
            :param (int) index: The index to insert the rows at
            """
            self.worksheet.insert_rows(rows, index)

    class SkyBlock:
        """
        An API handler for Hypixel's API
        """
        def __init__(self, key, session):
            self.key = key
            self.hypixel_url = "https://api.hypixel.net/"
            self.session = session

            self.skill_xp = Handlers.JSON.read("skills")
            self.skills = {
                "experience_skill_combat": "skyblock_combat",
                "experience_skill_mining": "skyblock_excavator",
                "experience_skill_alchemy": "skyblock_concoctor",
                "experience_skill_farming": "skyblock_harvester",
                "experience_skill_enchanting": "skyblock_augmentation",
                "experience_skill_fishing": "skyblock_angler",
                "experience_skill_foraging": "skyblock_gatherer"
            }

            self.pet_levels = Handlers.JSON.read("pet_rarity")

        async def api_request(self, endpoint: str, params: dict):
            """
            Makes an API request to the Hypixel API
            :param (str) endpoint: The endpoint to make the request to
            :param (dict) params: The parameters of the request
            :returns (dict) data: The output of the request
            :raises (Exception) error: Raises an Exception based on what cause Hypixel's API returns
            """
            async with self.session.get(self.hypixel_url + endpoint, params=params) as data:
                data = await data.text()
            data = json.loads(data)

            if data['success']:
                return data
            else:
                if data['cause'] == "Key throttle":
                    await asyncio.sleep(10)
                    await self.api_request(endpoint, params)
                else:
                    raise Exception(data['cause'])

        async def get_hypixel_profile(self, uuid):
            """
            Gets the Hypixel profile of a user
            :param (str) uuid: Player's UUID
            :returns (dict) profiles: Player's Hypixel profile
            """
            data = await self.api_request("player", {"key": self.key, "uuid": uuid})
            return data['player']

        async def get_profiles(self, uuid: str):
            """
            Gets all Hypixel SkyBlock profiles of a user
            :param (str) uuid: Player's UUID
            :returns (list) profiles: A list of all player's Hypixel SkyBlock profiles
            """
            data = await self.api_request("skyblock/profiles", {"key": self.key, "uuid": uuid})
            return data['profiles']

        async def get_unclaimed_auctions(self, profile_id: str):
            """
            Gets all Hypixel SkyBlock unclaimed auctions of a profile
            :param (str) profile_id: The ID of the profile
            :returns (list) auctions: The list of auctions for that profile ID
            """
            data = await self.api_request("skyblock/auction", {"key": self.key, "profile": profile_id})
            auctions = []
            ahs = data['auctions']
            for auction in ahs:
                if not auction['claimed']:
                    auctions.append(auction)
            return auctions

        async def get_auctions(self, page: int):
            """
            Gets Hypixel SkyBlock auctions
            :param (int) page: The page number, each page returns a dict with a list which has a 1000 auctions
            :returns (dict) data: The auction data
            """
            data = await self.api_request("skyblock/auctions", {"key": self.key, "page": page})
            return data

        async def get_bazaar_product(self, product_id: str):
            """
            Gets Hypixel SkyBlock bazaar information about a product
            :param (str) product_id: The ID of the product to get the information from
            :returns (dict) data: Bazaar product information
            """
            data = await self.api_request("skyblock/bazaar", {"key": self.key})
            return data['products'][product_id]

        async def get_guild(self, guild_id: str):
            """
            Gets information about a Hypixel guild
            :param (str) guild_id: The ID of the guild
            :returns (dict) data: Guild information
            """
            data = await self.api_request("guild", {"key": self.key, "id": guild_id})
            return data['guild']

        @staticmethod
        def calculate_latest_profile(profiles: list, uuid: str):
            """
            Calculates the latest Hypixel SkyBlock profile
            :param (list) profiles: A list of Hypixel SkyBlock profiles
            :param (str) uuid: The UUID of the person to check the latest profile
            :returns (dict) profile: The most recently used profile
            """
            profile_timestamps = {}
            profile_data = {}

            for profile in profiles:
                try:
                    last_save = profile['members'][uuid]['last_save']
                    last_save = datetime.fromtimestamp(last_save / 1000)
                    last_save_diff = (datetime.now() - last_save).total_seconds()
                    profile_id = profile['profile_id']
                    profile_timestamps[profile_id] = last_save_diff
                    profile_data[profile_id] = profile
                except KeyError:
                    pass
            profile_id = min(profile_timestamps, key=profile_timestamps.get)

            return profile_data[profile_id]

        def calculate_profile_skills(self, profile: dict, hypixel_profile: dict, uuid: str):
            """
            Calculates Hypixel SkyBlock profile's skills
            :param (dict) profile: The profile which should be used to calculate Hypixel SkyBlock skills
            :param (dict) hypixel_profile: Hypixel profile of the person
            :param (str) uuid: The UUID of the person to calculate the skills
            :returns (list) skill_levels: A list of all Hypixel SkyBlock profile's skills and the average skill level
            """
            player_profile = profile['members'][uuid]
            skill_levels = {}

            for skill in self.skills.keys():
                try:
                    xp = player_profile[skill]
                    if xp < self.skill_xp['1']:
                        skill_levels[skill] = 0
                        break

                    for i in range(50, 0, -1):
                        required_xp = self.skill_xp[str(i)]
                        if xp > required_xp:
                            skill_levels[skill] = i
                            break
                except KeyError:
                    try:
                        skill_levels[skill] = hypixel_profile['achievements'][self.skills[skill]]
                    except KeyError:
                        skill_levels[skill] = 0

            skill_levels['average_skill_level'] = sum(skill_levels.values()) / 7
            return skill_levels

        @staticmethod
        def calculate_profile_slayers(profile: dict, uuid: str):
            """
            Calculates Hypixel SkyBlock profile's slayers
            :param (dict) profile: The profile which should be used to calculate Hypixel SkyBlock slayers
            :param (str) uuid: The UUID of the person to calculate the slayers
            :returns (list) slayer_bosses: A list of all Hypixel SkyBlock profile's slayers and the total slayer xp
            """
            player_profile = profile['members'][uuid]
            slayers = player_profile['slayer_bosses']
            total_slayer_xp = 0
            slayer_bosses = {}

            for slayer_boss in slayers:
                if 'xp' in slayers[slayer_boss]:
                    money_spent = 0
                    tiers = [0, 1, 2, 3]
                    tier_money = [100, 2000, 10000, 50000]

                    for tier in tiers:
                        try:
                            money_spent += slayers[slayer_boss][f'boss_kills_tier_{tier}'] * tier_money[tier]
                        except KeyError:
                            pass

                    slayer_bosses[slayer_boss] = {"xp": slayers[slayer_boss]['xp'], "money_spent": money_spent}
                    total_slayer_xp += slayers[slayer_boss]['xp']
                else:
                    slayer_bosses[slayer_boss] = {"xp": 0, "money_spent": 0}
            slayer_bosses['total'] = total_slayer_xp
            return slayer_bosses

        def calculate_profile_pets(self, profile: dict, uuid: str):
            """
            Calculates Hypixel SkyBlock profile's pets
            :param (dict) profile: The profile which should be used to calculate Hypixel SkyBlock pets
            :param (str) uuid: The UUID of the person to calculate the pets
            :returns (dict) pets: A dict of pets and the information about them
            (level, xp, rarity, active, held_item, candy_used)
            """
            player_profile = profile['members'][uuid]
            pets = player_profile['pets']
            final_pets = {}

            for pet in pets:
                name = pet['type'].replace("_", " ").lower().title()
                exp = pet['exp']
                tier = pet['tier'].lower().title()
                active = pet['active']
                held_item = pet['heldItem']
                if held_item:
                    held_item = held_item.split("PET_ITEM_")[1].replace("_", " ").lower().title()
                candy_used = pet['candyUsed']

                # thanks to ComplexOrigin for this amazing way of getting levels
                # and thanks to Marti157 for helping me understand some parts of this
                pet_xp = self.pet_levels[tier.lower()].copy()
                pet_xp.append(exp)
                pet_xp.sort()
                level = pet_xp.index(exp)

                if exp == 0:
                    level = 1
                elif exp == 25353230:
                    level = 100

                final_pets[name] = {
                    "level": level,
                    "xp": exp,
                    "rarity": tier,
                    "active": active,
                    "held_item": held_item,
                    "candy_used": candy_used
                }
            return final_pets
