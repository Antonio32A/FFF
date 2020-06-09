import traceback

import aiohttp
import discord
from discord.ext import commands

from util.embed import Embed
from util.handlers import Handlers
from util.logging import Logger

config = Handlers.JSON.read("config")
logger = Logger(config['logging_level']).logger


class FFF(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.logger = logger
        self.session = aiohttp.ClientSession()

        self.base_extensions = [
            "general",
            "auction",
            "applications",
            "spreadsheet",
            "discord_sync"
        ]
        self.debug_extensions = [
            "owner"
        ]

    async def on_ready(self):
        # self.remove_command("help")
        await self.load_extensions()
        await self.update_activity()
        print(f"Logged in as {self.user} ({self.user.id}).")

    async def close(self):
        print("\nShutting down!")
        await super(FFF, self).close()
        await self.session.close()

    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        await self.process_commands(after)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
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
        if self.config['debug']:
            extensions = self.base_extensions + self.debug_extensions
        else:
            extensions = self.base_extensions

        for extension in extensions:
            self.load_extension(f"extensions.{extension}")
            print(f"Loaded {extension}.")
        print("Starting...")

    async def update_activity(self):
        activity = discord.Activity(
            name=self.config['activity']['name'],
            type=getattr(discord.ActivityType, self.config['activity']['type'])
        )
        await self.change_presence(activity=activity)


def get_pre(bot, message):
    # message is required for the get_pre to work properly
    bot_id = bot.user.id
    prefixes = [f"<@{bot_id}> ", f"<@!{bot_id}> ", bot.config['prefix']]
    return prefixes


fff = FFF(command_prefix=get_pre, owner_ids=(166630166825664512, 304979232814268417))
