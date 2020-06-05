import discord
from discord.ext import commands
from datetime import datetime
import re
import json

from disputils import BotEmbedPaginator
from util import Handlers


def insert(source_str: str, insert_str: str, pos: int):
    return source_str[:pos] + insert_str + source_str[pos:]


class Auction(commands.Cog, name="Auction"):
    """
    This cog adds Hypixel SkyBlock auction commands
    """
    def __init__(self, fff):
        self.fff = fff
        self.skyblock = Handlers.SkyBlock(self.fff.config['key'])
        self.mojang = Handlers.Mojang()

    @commands.command(hidden=True, aliases=['ah'])
    async def auction(self, ctx, username: str = None):
        """
        Display information about somebody's Hypixel SkyBlock unclaimed auctions.
        """
        if username is None:
            return await ctx.send("Invalid arguments. Please specify the argument username.")

        message = await ctx.send("Loading... Fetching UUID and profiles...")

        try:
            uuid = await self.mojang.get_player_uuid(username)
        except json.decoder.JSONDecodeError:
            await message.delete()
            return await ctx.send("That username doesn't exist!")

        profiles = await self.skyblock.get_profiles(uuid)
        if not profiles:
            await message.delete()
            return await ctx.send("That person doesn't have any profiles!")
        await message.edit(content="Loading... Fetched UUID and profiles, fetching profile auctions...")

        profile = self.skyblock.calculate_latest_profile(profiles, uuid)
        auctions = await self.skyblock.get_unclaimed_auctions(profile['profile_id'])
        await message.edit(content="Loading... Fetched profile auctions, creating embeds...")

        if not auctions:
            await message.delete()
            return await ctx.send("No unclaimed auctions.")
        embeds = []

        n = 0
        for auction in auctions:
            n += 1
            auction_id = str(auction['uuid'])
            auction_id = insert(auction_id, "-", 8)
            auction_id = insert(auction_id, "-", 13)
            auction_id = insert(auction_id, "-", 18)
            auction_id = insert(auction_id, "-", 23)

            embed = discord.Embed(color=ctx.author.color, title=f"{auction['item_name']} (Page {str(n)})")
            text = re.sub(r"§.", "", auction['item_lore'])
            embed.description = text

            ending_at = datetime.fromtimestamp(auction['end'] / 1000)
            ending_in = ending_at - datetime.now()

            if ending_in.total_seconds() < 0:
                ending_in = "Ended"
            else:
                ending_in = str(round(ending_in.total_seconds() / 60 / 60, 1)) + " hours"

            embed.add_field(name="Highest Bid:", value=f"{auction['highest_bid_amount']:,.0f}", inline=False)
            try:
                embed.add_field(name="Bidder Profile ID:", value=auction['bids'][-1]['bidder'], inline=False)
            except IndexError:
                pass

            embed.add_field(name="Ending in:", value=ending_in, inline=False)
            embed.add_field(name="Auction ID:", value=auction_id, inline=False)
            embeds.append(embed)

        await message.delete()
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()
