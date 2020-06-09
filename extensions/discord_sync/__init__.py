from .discord_sync import DiscordSync


def setup(fff):
    fff.add_cog(DiscordSync(fff))
