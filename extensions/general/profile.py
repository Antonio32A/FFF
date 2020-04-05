import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime
import re

from disputils import BotEmbedPaginator
from util import Handlers

class Profile(commands.Cog, name="Profile"):
    def __init__(self, fff):
        self.fff = fff
        self.api = Handlers.Skyblock(self.fff.config["key"])
        with open("skills.json") as file:
            self.skill_xp = json.load(file)
        self.emojis = self.fff.config["emojis"]

        self.pet_levels_common = [0, 100, 210, 330, 460, 605, 765, 940, 1130, 1340, 1570, 1820, 2095, 2395, 2725, 3085, 3485, 3925, 4415, 4955, 5555, 6215, 6945, 7745, 8625, 9585, 10635, 11785, 13045, 14425, 15935, 17585, 19385, 21345, 23475, 25785, 28285, 30985, 33905, 37065, 40485, 44185, 48185, 52535, 57285, 62485, 68185, 74485, 81485, 89285, 97985, 107685, 118485, 130485, 143785, 158485, 174685, 192485, 211985, 233285, 256485, 281685, 309085, 338885, 371285, 406485, 444685, 486085, 530885, 579285, 631485, 687685, 748085, 812885, 882285, 956485, 1035685, 1120385, 1211085, 1308285, 1412485, 1524185, 1643885, 1772085, 1909285, 2055985, 2212685, 2380385, 2560085, 2752785, 2959485, 3181185, 3418885, 3673585, 3946285, 4237985, 4549685, 4883385, 5241085, 5624785, 6036485, 6478185, 6954885, 7471585, 8033285, 8644985, 9311685, 10038385, 10830085, 11691785, 12628485, 13645185, 14746885, 15938585, 17225285, 18611985, 20108685, 21725385, 23472085, 25358785]
        self.pet_levels_uncommon = [0, 175, 365, 575, 805, 1055, 1330, 1630, 1960, 2320, 2720, 3160, 3650, 4190, 4790, 5450, 6180, 6980, 7860, 8820, 9870, 11020, 12280, 13660, 15170, 16820, 18620, 20580, 22710, 25020, 27520, 30220, 33140, 36300, 39720, 43420, 47420, 51770, 56520, 61720, 67420, 73720, 80720, 88520, 97220, 106920, 117720, 129720, 143020, 157720, 173920, 191720, 211220, 232520, 255720, 280920, 308320, 338120, 370520, 405720, 443920, 485320, 530120, 578520, 630720, 686920, 747320, 812120, 881520, 955720, 1034920, 1119620, 1210320, 1307520, 1411720, 1523420, 1643120, 1771320, 1908520, 2055220, 2211920, 2379620, 2559320, 2752020, 2958720, 3180420, 3418120, 3672820, 3945520, 4237220, 4548920, 4882620, 5240320, 5624020, 6035720, 6477420, 6954120, 7470820, 8032520, 8644220, 9310920]
        self.pet_levels_rare = [0, 275, 575, 905, 1265, 1665, 2105, 2595, 3135, 3735, 4395, 5125, 5925, 6805, 7765, 8815, 9965, 11225, 12605, 14115, 15765, 17565, 19525, 21655, 23965, 26465, 29165, 32085, 35245, 38665, 42365, 46365, 50715, 55465, 60665, 66365, 72665, 79665, 87465, 96165, 105865, 116665, 128665, 141965, 156665, 172865, 190665, 210165, 231465, 254665, 279865, 307265, 337065, 369465, 404665, 442865, 484265, 529065, 577465, 629665, 685865, 746265, 811065, 880465, 954665, 1033865, 1118565, 1209265, 1306465, 1410665, 1522365, 1642065, 1770265, 1907465, 2054165, 2210865, 2378565, 2558265, 2750965, 2957665, 3179365, 3417065, 3671765, 3944465, 4236165, 4547865, 4881565, 5239265, 5622965, 6034665, 6476365, 6953065, 7469765, 8031465, 8643165, 9309865, 10036565, 10828265, 11689965, 12626665, 13643365]
        self.pet_levels_epic = [0, 440, 930, 1470, 2070, 2730, 3460, 4260, 5140, 6100, 7150, 8300, 9560, 10940, 12450, 14100, 15900, 17860, 19990, 22300, 24800, 27500, 30420, 33580, 37000, 40700, 44700, 49050, 53800, 59000, 64700, 71000, 78000, 85800, 94500, 104200, 115000, 127000, 140300, 155000, 171200, 189000, 208500, 229800, 253000, 278200, 305600, 335400, 367800, 403000, 441200, 482600, 527400, 575800, 628000, 684200, 744600, 809400, 878800, 953000, 1032200, 1116900, 1207600, 1304800, 1409000, 1520700, 1640400, 1768600, 1905800, 2052500, 2209200, 2376900, 2556600, 2749300, 2956000, 3177700, 3415400, 3670100, 3942800, 4234500, 4546200, 4879900, 5237600, 5621300, 6033000, 6474700, 6951400, 7468100, 8029800, 8641500, 9308200, 10034900, 10826600, 11688300, 12625000, 13641700, 14743400, 15935100, 17221800, 18608500, 20105200]
        self.pet_levels_legendary = [0, 660, 1390, 2190, 3070, 4030, 5080, 6230, 7490, 8870, 10380, 12030, 13830, 15790, 17920, 20230, 22730, 25430, 28350, 31510, 34930, 38630, 42630, 46980, 51730, 56930, 62630, 68930, 75930, 83730, 92430, 102130, 112930, 124930, 138230, 152930, 169130, 186930, 206430, 227730, 250930, 276130, 303530, 333330, 365730, 400930, 439130, 480530, 525330, 573730, 625930, 682130, 742530, 807330, 876730, 950930, 1030130, 1114830, 1205530, 1302730, 1406930, 1518630, 1638330, 1766530, 1903730, 2050430, 2207130, 2374830, 2554530, 2747230, 2953930, 3175630, 3413330, 3668030, 3940730, 4232430, 4544130, 4877830, 5235530, 5619230, 6030930, 6472630, 6949330, 7466030, 8027730, 8639430, 9306130, 10032830, 10824530, 11686230, 12622930, 13639630, 14741330, 15933030, 17219730, 18606430, 20103130, 21719830, 23466530, 25353230]

    def insert(self, source_str: str, insert_str: str, pos: int):
        return source_str[:pos]+insert_str+source_str[pos:]

    @commands.command(hidden=True, aliases=["ah"])
    async def auction(self, ctx, username: str=None, profile_name: str=None):
        if username == None:
            return await ctx.send("Invalid arguments. Please specify your username.")

        message = await ctx.send("Loading... This might take a few seconds.")
        try:
            uuid = await self.api.get_player_uuid(username)
            profile_ids = await self.api.get_skyblock_profile_ids(uuid)
        except:
            return await ctx.send("An error has occured!\nYour API might be off, Hypixel/Mojang API might be down or your username is incorrect.")

        if profile_name == None:
            profile_timestamps = {}
            for profile_id in profile_ids:
                profile = await self.api.get_skyblock_profile(uuid, profile_ids[profile_id])
                last_save = profile["members"][uuid]["last_save"]
                last_save = datetime.fromtimestamp(last_save/1000)
                last_save_diff = (datetime.now() - last_save).total_seconds()
                profile_timestamps[profile_id] = last_save_diff
            profile_name = min(profile_timestamps, key=profile_timestamps.get)

        try:
            profile_name = profile_name.capitalize()
            profile_id = profile_ids[profile_name]
            auctions = await self.api.get_skyblock_unclaimed_auctions(profile_id)
            player = profile["members"][uuid]
        except:
            return await ctx.send("An error has occured!\nYour API might be off or the profile name/username might be incorrect.")

        if auctions == []:
            await message.delete()
            return await ctx.send("No unclaimed auctions.")
        embeds = []

        n = 0
        for auction in auctions:
            n += 1
            id = str(auction["uuid"])
            id = self.insert(id, "-", 8)
            id = self.insert(id, "-", 13)
            id = self.insert(id, "-", 18)
            id = self.insert(id, "-", 23)

            embed = discord.Embed(color=ctx.author.color, title= f"{auction['item_name']} (Page {str(n)})")
            text = auction["item_lore"]
            text = re.sub(r"\§.", "", auction["item_lore"])
            embed.description = text

            ending_at = datetime.fromtimestamp(auction["end"]/1000)
            ending_in = ending_at - datetime.now()

            if ending_in.total_seconds() < 0:
                ending_in = "Ended"
            else:
                ending_in = str(round(ending_in.total_seconds()/60/60, 1)) + " hours"

            embed.add_field(name="Highest Bid:", value=f"{auction['highest_bid_amount']:,.0f}", inline=False)
            try:
                embed.add_field(name="Bidder Profile ID:", value=auction['bids'][-1]['bidder'], inline=False)
            except:
                pass
            embed.add_field(name="Ending in:", value=ending_in, inline=False)
            embed.add_field(name="Auction ID:", value=id, inline=False)
            embeds.append(embed)

        await message.delete()
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()



    @commands.command()
    async def profile(self, ctx, username: str=None, profile_name: str=None):
        if username == None:
            return await ctx.send("Invalid arguments. Please specify your username.")

        message = await ctx.send("Loading... This might take a few seconds.")
        try:
            uuid = await self.api.get_player_uuid(username)
            profile_ids = await self.api.get_skyblock_profile_ids(uuid)
            embeds = []
        except:
            return await ctx.send("An error has occured!\nYour API might be off, Hypixel/Mojang API might be down or your username is incorrect.")

        if profile_name == None:
            profile_timestamps = {}
            for profile_id in profile_ids:
                profile = await self.api.get_skyblock_profile(uuid, profile_ids[profile_id])
                last_save = profile["members"][uuid]["last_save"]
                last_save = datetime.fromtimestamp(last_save/1000)
                last_save_diff = (datetime.now() - last_save).total_seconds()
                profile_timestamps[profile_id] = last_save_diff
            profile_name = min(profile_timestamps, key=profile_timestamps.get)

        try:
            profile_name = profile_name.capitalize()
            profile_id = profile_ids[profile_name]
            profile = await self.api.get_skyblock_profile(uuid, profile_id)
            player = profile["members"][uuid]
        except:
            return await ctx.send("An error has occured!\nYour API might be off or the profile name/username might be incorrect.")

        # Bank Balance and Fairy Souls
        try:
            bank = round(float(profile["banking"]["balance"]), 1)
        except:
            return await ctx.send("An error has occured!\nPlease turn `Bank` API ON and try again...")

        fairy_souls = player["fairy_souls_collected"]
        bank = f"{self.emojis['bank']} | **Bank Balance:** `{bank:,.0f}`"
        fairy_souls = f"{self.emojis['fairysouls']} | **Fairy Souls:** `{fairy_souls}/190`"

        last_logged_in = datetime.fromtimestamp(player["last_save"]/1000)
        last_logged_in_diff = datetime.now() - last_logged_in
        last_logged_in = f":clock1: | Last logged in {round(last_logged_in_diff.total_seconds()/60/60, 1)} hours ago"

        main = discord.Embed(title=f"{self.emojis['profile']} {username}'s Skyblock Profile.", description=fairy_souls + "\n" + bank + "\n" + last_logged_in, color=ctx.author.color)
        embeds.append(main)

        # Skills
        skills_embed = discord.Embed(title=f"{self.emojis['combat']} {username}'s Skyblock Skills.", color=ctx.author.color)
        skills = ["experience_skill_combat", "experience_skill_mining", "experience_skill_alchemy", "experience_skill_farming", "experience_skill_enchanting", "experience_skill_fishing", "experience_skill_foraging"]
        skill_names = [f"{self.emojis['combat']} | Combat", f"{self.emojis['mining']} | Mining", f"{self.emojis['alchemy']} | Alchemy", f"{self.emojis['farming']} | Farming", f"{self.emojis['enchanting']} | Enchanting", f"{self.emojis['fishing']} | Fishing", f"{self.emojis['foraging']} | Foraging"]
        skill_levels = {}

        for skill in skills:
            xp = player[skill]
            for i in range(50, 0, -1):
                required_xp = self.skill_xp[str(i)]
                if xp > required_xp:
                    skill_levels[skill] = i
                    break

        # Average Skill Level
        average_skill_level = 0.0
        for skill, skill_name in zip(skill_levels, skill_names):
            average_skill_level += skill_levels[skill]
            skills_embed.add_field(name=str(skill_name), value=f"`{str(skill_levels[skill])}`", inline=True)

        skills_embed.add_field(name="\u200B\nTotal Average:", value=f"**{round(average_skill_level/7, 1)}**", inline=False)
        embeds.append(skills_embed)

        # Slayers
        total_slayer_xp = 0
        slayer_bosses = {}
        for slayer_boss in player["slayer_bosses"]:
            money_spent = 0
            tiers = [0, 1, 2, 3]
            tier_money = [100, 2000, 10000, 50000]
            for tier in tiers:
                try:
                    money_spent += player["slayer_bosses"][slayer_boss][f"boss_kills_tier_{tier}"]*tier_money[tier]
                except:
                    pass
            slayer_bosses[slayer_boss] = {"xp": player["slayer_bosses"][slayer_boss]["xp"],
                                            "money_spent": money_spent}
            total_slayer_xp += player["slayer_bosses"][slayer_boss]["xp"]
        slayers = discord.Embed(title=f"{self.emojis['slayer']} {username}'s Skyblock Slayers.", color=ctx.author.color)

        def format_slayer_info(slayer_name: str):
            info = f"XP: {slayer_bosses[slayer_name]['xp']:,.0f}\n" + f"Money Spent: {slayer_bosses[slayer_name]['money_spent']:,.0f}"
            return info

        slayers.add_field(name=f"{self.emojis['zombie']} | Reventant Horror", value=format_slayer_info("zombie"), inline=False)
        slayers.add_field(name=f"{self.emojis['spider']} | Tarantula Broodfather", value=format_slayer_info("spider"), inline=False)
        slayers.add_field(name=f"{self.emojis['wolf']} | Sven Packmaster", value=format_slayer_info("wolf"), inline=False)
        slayers.add_field(name=f"{self.emojis['slayer']} | Total Slayer XP", value=f"{total_slayer_xp:,.0f}")
        embeds.append(slayers)

        pet_text = ""
        pets = player["pets"]
        for pet in pets:
            name = pet["type"].replace("_", " ").lower().title()
            exp = pet["exp"]
            tier = pet["tier"].lower().title()
            active = pet["active"]
            # all credits go to ComplexOrigin for this amazing way of getting levels, also thanks to Marti157 for helping me understand some parts of this
            if tier == "Common":
                pet_xp = self.pet_levels_common.copy()
            elif tier == "Uncommon":
                pet_xp = self.pet_levels_uncommon.copy()
            elif tier == "Rare":
                pet_xp = self.pet_levels_rare.copy()
            elif tier == "Epic":
                pet_xp = self.pet_levels_epic.copy()
            elif tier == "Legendary":
                pet_xp = self.pet_levels_legendary.copy()
            pet_xp.append(exp)
            pet_xp.sort()
            level = pet_xp.index(exp)

            if exp == 0:
                level = 1
            elif exp == 25353230:
                level = 100

            if active == False:
                pet_text += f"[{str(level)}] {name} - {tier}\n"
            else:
                pet_text += f"**[{str(level)}] {name} - {tier}**\n"

        pet_embed = discord.Embed(title=f"{username}'s Pets", color=ctx.author.color)
        pet_embed.description = pet_text
        embeds.append(pet_embed)

        await message.delete()
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()
