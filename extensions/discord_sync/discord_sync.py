import asyncio

import discord
from discord.ext import commands, tasks


class DiscordSync(commands.Cog, name="DiscordSync"):
    def __init__(self, fff):
        self.fff = fff

        self.guild = self.fff.get_guild(self.fff.config['discord_guild']['id'])
        self.roles = self.fff.config['roles']
        self.discord_sync_loop.start()

    def cog_unload(self):
        """
        In case the cog unloads, cancel the loop
        """
        self.discord_sync_loop.cancel()

    @tasks.loop(minutes=15.0)
    async def discord_sync_loop(self):
        """
        Automatically gets all the guild members and assigns them the roles in Discord
        """
        try:
            guild_data = self.fff.cache.get()['guild_data']
        except KeyError:
            return  # This only happens when the bot starts since the data isn't cached yet

        self.fff.logger.info("Syncing Discord roles and Hypixel guild ranks...")
        all_roles = {}
        for role in self.roles.values():
            all_roles[role] = []

        for member in guild_data.keys():
            uuid = member
            member = guild_data[uuid]
            username = member['username']
            discord_connection = member['discord_connection']
            rank = member['rank']

            if discord_connection is None:
                self.fff.logger.warning(
                    f"{username} ({uuid}) with the rank {rank} does not have their Discord "
                    f"connected!"
                )
                continue

            try:
                role = self.roles[rank]
            except KeyError:
                continue  # role doesn't exist

            discord_member = self.guild.get_member_named(discord_connection)
            if discord_member is not None:
                # gets all the roles before the highest one
                for i in range(list(self.roles.values()).index(role) + 1):
                    role = list(self.roles.values())[i]
                    all_roles[role].append(discord_member.id)

        for role in all_roles.keys():
            discord_role = self.guild.get_role(int(role))
            for member in discord_role.members:
                # This part could be improved by just adding a list of roles to one person, but it's not really needed
                # since this runs every 10 minutes which is more than enough time to execute it
                if member.id not in all_roles[role]:
                    try:
                        await member.remove_roles(discord_role)
                        self.fff.logger.info(f"[-] {discord_role.name} -> {member.name}")
                        await asyncio.sleep(1)
                    except (discord.Forbidden, discord.NotFound):
                        self.fff.logger.warning(f"Could not remove {discord_role.name} from {member.name}!")

            for member_id in all_roles[role]:
                member = self.guild.get_member(member_id)
                if discord_role not in member.roles:
                    try:
                        await member.add_roles(discord_role)
                        self.fff.logger.info(f"[+] {discord_role.name} -> {member.name}")
                        await asyncio.sleep(1)
                    except (discord.Forbidden, discord.NotFound):
                        self.fff.logger.warning(f"Could not add {discord_role.name} to {member.name}!")

        self.fff.logger.info("Successfully synced all the Discord roles to Hypixel guild ranks.")

    @discord_sync_loop.before_loop
    async def before_tasks(self):
        """
        This starts the loop when the bot is ready to work
        """
        await self.fff.wait_until_ready()
