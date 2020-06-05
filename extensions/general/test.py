import discord
from discord.ext import commands
from util import Handlers


class Test(commands.Cog, name="Test"):
    """
    This cog is used to test random stuff and it's just so I don't have to create a new cog every time I want to test
    a feature or two. Also random commands will probably be added here.
    """
    def __init__(self, fff):
        self.fff = fff
        self.skyblock = Handlers.SkyBlock(self.fff.config['key'])
        self.materials = [
            "LOG",
            "BROWN_MUSHROOM",
            "RED_MUSHROOM",
            "REDSTONE",
            "GLOWSTONE_DUST"
        ]

    @commands.command()
    async def soup(self, ctx, amount: int = 1):
        """
        Shows Hypixel SkyBlock bazaar soup prices
        """
        loading = await ctx.send("Loading...")
        mats = {}
        total = 0

        for material in self.materials:
            cost = (await self.skyblock.get_bazaar_product(material))['quick_status']['sellPrice']
            if material == "LOG":
                cost = cost / (4 / (3 / 4))
            mats[material] = cost
            total += cost * amount

        embed = discord.Embed(title="Soups!", color=ctx.author.color)
        embed.description = f"Total amount of money needed to create **{amount}** soup(s) is ~**{round(total)}** coins!"

        for mat in mats:
            embed.add_field(
                name=f"{amount}x **{mat.lower().replace('_', ' ')}**",
                value=f"~**{round(mats[mat] * amount)}** coins (or ~**{round(mats[mat])}** coins each)",
                inline=False
            )

        await ctx.send(embed=embed)
        await loading.delete()
