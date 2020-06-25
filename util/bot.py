import argparse
import traceback

import aiohttp
import discord
from discord.ext import commands

from util.embed import Embed
from util.handlers import Handlers
from util.logging import Logger
from util.cache import Cache
from util.database import Database

parser = argparse.ArgumentParser(description="Runs the FFF bot")
parser.add_argument(
    "--debug",
    help="Add this argument if you wish to run the bot in debug mode which changes the token, prefix and loads some "
         "debug modules.",
    action="store_true"
)

debug = parser.parse_args().debug
logging_level = "DEBUG" if debug else "INFO"
logger = Logger(level=logging_level).logger

config = Handlers.JSON.read("config")


class FFF(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.bot_config = self.config['bot']
        self.session = aiohttp.ClientSession()
        self.logger = logger
        self.cache = Cache()
        self.database = Database(self.config['database'])
        self.pool = None
        self.debug = debug
        self.title = self.bot_config['title']

        self.base_extensions = self.bot_config['extensions']['base']
        self.debug_extensions = self.bot_config['extensions']['debug']

        if self.debug:
            self.bot_extensions = self.base_extensions + self.debug_extensions
            self.token = self.bot_config['debug_token']
            self.prefix = self.bot_config['debug_prefix']
        else:
            self.bot_extensions = self.base_extensions
            self.token = self.bot_config['production_token']
            self.prefix = self.bot_config['production_prefix']

    async def on_ready(self):
        # self.remove_command("help")
        self.pool = await self.database.connect()
        await self.update_cache()
        await self.load_extensions()
        await self.update_activity()

        self.logger.info(f"Logged in as {self.user} ({self.user.id}).")
        if self.debug:
            self.logger.critical("Starting in debug mode, do not use this in production!")

    async def close(self):
        self.logger.info("\nShutting down!")
        await super(FFF, self).close()
        await self.session.close()
        await self.pool.close()

    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        await self.process_commands(after)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Invalid command arguments!")
        else:
            try:
                raise error
            except Exception as error:
                cause = str(error.__cause__)
                owner = self.get_user(self.owner_ids[0])
                length = 1024 - (len(cause) + 3)

                embed = Embed(title="An error has occurred!", color=ctx.author.color)
                embed.add_field(
                    name=cause,
                    value=str(traceback.format_exc()[:length]) + "...",
                    inline=False
                )
                embed.add_field(name="Command name", value=ctx.command.qualified_name, inline=False)
                embed.add_field(name="Executed by", value=f"`{ctx.author}` ({ctx.author.id})", inline=False)
                embed.add_field(
                    name="Executed in",
                    value=f"`{ctx.guild.name}` ({ctx.guild.id})\n"
                          f"<#{ctx.channel.id}> (`{ctx.channel.name}`, {ctx.channel.id})",
                    inline=False
                )
                await owner.send(embed=embed)

                embed = Embed(title="An error has occurred!", color=ctx.author.color)
                embed.add_field(name=cause, value="The owner has been notified about this error.")
                await ctx.send(embed=embed)
                self.logger.error(traceback.format_exc())

    async def load_extensions(self):
        for extension in self.bot_extensions:
            self.load_extension(f"extensions.{extension}")
            self.logger.info(f"Loaded {extension}.")
        self.logger.info("Starting...")

    async def update_activity(self):
        activity = discord.Activity(
            name=self.config['bot']['activity']['name'],
            type=getattr(discord.ActivityType, self.config['bot']['activity']['type'])
        )
        await self.change_presence(activity=activity)

    async def update_cache(self):
        self.logger.debug("Updating cache...")
        async with self.pool.acquire() as conn:
            guild_data = await self.database.get_guild_data(conn)
            guild_data_history = await self.database.get_guild_data_history(conn)
            self.cache.set(
                {
                    "guild_data": guild_data,
                    "guild_data_history": guild_data_history
                }
            )
        self.logger.debug("Successfully updated the cache!")


def get_pre(bot, message):
    bot_id = bot.user.id
    prefixes = [f"<@{bot_id}> ", f"<@!{bot_id}> ", bot.prefix]
    return prefixes


fff = FFF(command_prefix=get_pre, owner_ids=tuple(config['bot']['owners']))
