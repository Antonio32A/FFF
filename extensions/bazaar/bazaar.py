import discord
from discord.ext import commands, tasks
from datetime import datetime

import matplotlib.pyplot as plt
from util import Handlers

class Bazaar(commands.Cog, name="Bazaar"):
    def __init__(self, fff):
        self.fff = fff
        self.api = Handlers.Skyblock(self.fff.config["key"])
        self.sell_prices = []
        self.buy_prices = []
        self.time = []
        self.stonks.start()

    @tasks.loop(seconds=30.0)
    async def stonks(self):
        stonks = (await self.api.get_skyblock_bazaar("STOCK_OF_STONKS"))["product_info"]
        buy_price = round(stonks["quick_status"]["sellPrice"])
        sell_price = round(stonks["quick_status"]["buyPrice"])
        self.sell_prices.append(sell_price)
        self.buy_prices.append(buy_price)
        self.time.append(datetime.now())

        plt.xlabel("Time", color="magenta", weight="bold", fontsize=12)
        plt.ylabel("Stonks Sell Price", color="magenta", weight="bold", fontsize=12)
        plt.plot(self.time, self.buy_prices, linestyle="-", color="springgreen")
        plt.plot(self.time, self.sell_prices, linestyle="-", color="tomato")
        plt.title(f"Buy Price: {buy_price:,}", loc="left", fontsize=15, weight="bold", color="springgreen")
        plt.title(f"Sell Price: {sell_price:,}", loc="right", fontsize=12, weight="bold", color="tomato")
        plt.savefig("graph.png")

        guild = self.fff.get_guild(self.fff.config["guild"])
        channel = guild.get_channel(self.fff.config["bazaar_channel"])
        await channel.purge(limit=1)
        await channel.send(file=discord.File("graph.png"))
