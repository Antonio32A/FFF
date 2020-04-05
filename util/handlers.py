import json
import asyncio
import aiohttp

class Handlers:
    class JSON:
        def __init__(self, fff):
            self.fff = fff

        def read(file):
            with open(f"{file}.json", "r", encoding="utf8") as file:
                data = json.load(file)
            return data

        def dump(file, data):
            with open(f"{file}.json", "w", encoding="utf8") as file:
                    json.dump(data, file, indent=4)

    class Skyblock:
        def __init__(self, key):
            self.key = key
            self.hypixel_url = "https://api.hypixel.net/"

        async def skyblock_api_request(self, endpoint: str, params: dict):
            async with aiohttp.ClientSession() as session:
                    async with session.get(self.hypixel_url + endpoint, params=params) as data:
                        data = await data.text()
            return json.loads(data)

        async def get_player_uuid(self, username: str):
            async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as data:
                        data = await data.text()
            return json.loads(data)["id"]

        async def get_skyblock_profile(self, uuid: str, profile_id: str):
            data = await self.skyblock_api_request("skyblock/profile", {"key": self.key, "profile": profile_id})
            return data["profile"]

        async def get_skyblock_profile_ids(self, uuid: str):
            data = await self.skyblock_api_request("player", {"key": self.key, "uuid": uuid})
            profile_ids = data["player"]["stats"]["SkyBlock"]["profiles"]
            new_profile_ids = {}
            for profile in profile_ids:
                new_profile_ids[profile_ids[profile]["cute_name"]] = profile
            return new_profile_ids

        async def get_skyblock_unclaimed_auctions(self, profile_id: str):
            data = await self.skyblock_api_request("skyblock/auction", {"key": self.key, "profile": profile_id})
            ahs = []
            auctions = data["auctions"]
            for i in auctions:
                if i["claimed"] == False:
                    ahs.append(i)
            return ahs

        async def get_skyblock_auctions(self, page: int):
            data = await self.skyblock_api_request("skyblock/auctions", {"key": self.key, "page": page})
            return data

        async def get_skyblock_bazaar(self, productId: str):
            data = await self.skyblock_api_request("skyblock/bazaar/product", {"key": self.key, "productId": productId})
            return data

        async def get_guild(self, guildId: str):
            data = await self.skyblock_api_request("guild", {"key": self.key, "id": guildId})
            return data["guild"]
