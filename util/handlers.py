import json
import asyncio
import aiohttp
import base64

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

        async def get_player_uuid(self, username: str):
            async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as data:
                        data = await data.text()
            return json.loads(data)["id"]

        async def get_skyblock_profile(self, uuid: str, profile_id: str):
            async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.hypixel.net/skyblock/profile", params={"key": self.key, "profile": profile_id}) as data:
                        data = await data.text()
            return json.loads(data)["profile"]

        async def get_guild(self, guild_id: str):
            async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.hypixel.net/guild", params={"key": self.key, "guild_id": guild_id}) as data:
                        data = await data.text()
            return json.loads(data)["guild"]

        async def get_skyblock_profile_ids(self, uuid: str):
            async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.hypixel.net/player", params={"key": self.key, "uuid": uuid}) as data:
                        data = await data.text()
            profile_ids = json.loads(data)["player"]["stats"]["SkyBlock"]["profiles"]
            new_profile_ids = {}
            for profile in profile_ids:
                new_profile_ids[profile_ids[profile]["cute_name"]] = profile
            return new_profile_ids

        async def get_skyblock_unclaimed_auctions(self, profile_id: str):
            async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.hypixel.net/skyblock/auction", params={"key": self.key, "profile": profile_id}) as data:
                        data = await data.text()
            ahs = []
            auctions = json.loads(data)["auctions"]
            for i in auctions:
                if i["claimed"] == False:
                    ahs.append(i)
            return ahs
