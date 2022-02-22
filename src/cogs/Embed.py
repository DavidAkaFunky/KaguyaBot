import discord, json, re
from Data_classes import AnimeData, MangaData
from discord.ext.commands import Cog, Bot
from os import environ
from discord_slash import cog_ext
from Requests import make_request
from datetime import datetime

class Embed (Cog):

    def __init__(self,bot):
        self.bot = bot   


    ########################## MISCELLANEOUS ##########################

    async def get_empty_embed(self, ctx):
        embed = discord.Embed(title = "‎")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        return msg

    async def get_reaction(self, msg, index, length):
        def check(reaction, user):
            return str(reaction.emoji) in ["⬅", "➡"]
        reaction, user = await self.bot.wait_for('reaction_add', check=check)
        if str(reaction.emoji) == "➡":
            index = (index + 1) % length
            await msg.remove_reaction("➡", user)
        elif str(reaction.emoji) == "⬅":
            index = (index - 1) % length
            await msg.remove_reaction("⬅", user)
        return index
    

    ########################## INDIVIDUAL ENTRY COMMANDS ##########################

    async def get_search_entry_embed(self, ctx, msg, data, content, username, index, length):
        entry = data.get_entry(content[index])
        embed = discord.Embed(title = entry[0][0], color = 0x26448f if content[index]["status"].split()[0] == "Finished" else 0x2db039)
        for i in range(1, len(entry[0])):
            embed.add_field(name=data.get_search_header()[i], value=entry[0][i] if entry[0][i] != "" else "N/A")
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(entry[1]), inline=False)
        embed.set_image(url=entry[2])
        embed.set_footer(text="Search result {} of {}".format(index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def get_search_embed(self, ctx, data, username):    
        search = data.get_search()
        msg = await self.get_empty_embed(ctx)
        index = 0
        length = len(search)
        while True:
            await self.get_search_entry_embed(ctx, msg, data, search, username, index, length)
            index = await self.get_reaction(msg, index, length)

    async def get_search(self, ctx, data, name):
        if await data.fetch_search(name):
            await self.get_search_embed(ctx, data, name)

    @cog_ext.cog_slash(name="manga", guild_ids=eval(environ["GUILDS"]))
    async def get_manga(self, ctx, name):
        """Search for manga"""
        await self.get_search(ctx, MangaData(), name)

    @cog_ext.cog_slash(name="anime", guild_ids=eval(environ["GUILDS"]))
    async def get_anime(self, ctx, name):
        """Search for anime"""
        await self.get_search(ctx, AnimeData(), name)


    ########################## LIST COMMANDS ##########################

    async def get_list_entry_embed(self, ctx, msg, data, content, username, index, length):
        status = "watching_status" if "watching_status" in content[index] else "reading_status"
        entry = data.get_element(content[index])
        embed = discord.Embed(title = entry[0][0], color = data.get_status()[content[index][status]][1])
        for i in range(1, len(entry[0])):
            if status == "watching_status" and i == 7:
                continue
            embed.add_field(name=data.get_header()[i], value=entry[0][i] if entry[0][i] != "" else "N/A")
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(entry[1]), inline=False)
        embed.set_image(url=entry[2])
        embed.set_footer(text="{}'s {} list: Entry {} of {}".format(username.capitalize(), data.get_info()["type"], index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def get_list_embed(self, ctx, data, username):      
        table = data.get_table()
        msg = await self.get_empty_embed(ctx)
        index = 0
        length = len(table)
        while True:
            await self.get_list_entry_embed(ctx, msg, data, table, username, index, length)
            index = await self.get_reaction(msg, index, length)

    async def get_list(self, ctx, data, username):
        """Send embed anime list"""
        if await data.fetch_list(username):
            await self.get_list_embed(ctx, data, username)

    @cog_ext.cog_slash(name="animelist", guild_ids=eval(environ["GUILDS"]))
    async def get_anime_list(self, ctx, username):
        """Send username's anime list"""
        await self.get_list(ctx, AnimeData(), username)

    @cog_ext.cog_slash(name="mangalist", guild_ids=eval(environ["GUILDS"]))
    async def get_manga_list(self, ctx, username):
        """Show username's manga list"""
        await self.get_list(ctx, MangaData(), username)
    
    async def get_character_pic_embed(self, ctx, embed, msg, pics, index, length):
        embed.set_image(url=pics[index])
        embed.set_footer(text="Picture {} of {}".format(index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def get_character_embed(self, ctx, character, pics):
        def get_nicknames(nicknames):
            res = ""
            if nicknames == []:
                return "N/A"
            for el in nicknames:
                res += el + ", "
            return res[:-2]
        def get_about(character):
            res = ""
            for el in re.split(r"[.\n]", character["about"]):
                if el == "":
                    continue
                el += ". "
                if len(res) + len(el) >= 1025:
                    return res[:-1]
                res += el
        embed = discord.Embed(title = character["name"], color = 0x26448f)
        embed.add_field(name="Nickname", value=get_nicknames(character["nicknames"]))
        embed.add_field(name="Favourites", value=character["favorites"])
        embed.add_field(name="About", value=get_about(character), inline=False)
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(character["url"]), inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        index = 0
        length = len(pics)
        while True:
            await self.get_character_pic_embed(ctx, embed, msg, pics, index, length)
            index = await self.get_reaction(msg, index, length)

    @cog_ext.cog_slash(name="character", guild_ids=eval(environ["GUILDS"]))
    async def get_character(self, ctx, name):
        """Search for anime/manga character"""
        (b, r) = await make_request("https://api.jikan.moe/v4/characters?q={}&sfw&order_by=popularity".format(name))
        if not b:
            return
        character = json.loads(r.content)["data"][0]
        (b, r) = await make_request("https://api.jikan.moe/v4/characters/{}/pictures".format(character["mal_id"]))
        if not b:
            return
        pics = [pic["jpg"]["image_url"] for pic in json.loads(r.content)["data"]]
        main = character["images"]["jpg"]["image_url"]
        try:
            pics.remove(main)
        except:
            pass
        pics = [main] + pics
        await self.get_character_embed(ctx, character, pics)


    ########################## USER COMMANDS ##########################

    async def get_user_page_embed(self, ctx, msg, data, index, length):
        def get_colour(gender):
            if gender == "Male":
                return 0x26448f
            elif gender == "Female":
                return 0xff8da1
            return 0xffbf00
        entry = data[index]
        options = ["user info", "anime data", "manga data"]
        embed = discord.Embed(title = "{}'s {}".format(data[0][0], options[index]), color = get_colour(data[0][1]["Gender"]))
        lst = entry[1] if index == 0 else entry
        for key in lst:
            embed.add_field(name=key, value=lst[key] if lst[key] != None else "N/A")
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(data[0][2]), inline=False)
        embed.set_image(url=data[0][3])
        embed.set_footer(text="Click left for {}\nClick right for {}".format(options[(index-1)%length], options[(index+1)%length]), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def get_user_embed(self, ctx, user, anime, manga):    
        data = (user, anime, manga)
        msg = await self.get_empty_embed(ctx)
        index = 0
        length = len(data)
        while True:
            await self.get_user_page_embed(ctx, msg, data, index, length)
            index = await self.get_reaction(msg, index, length)

    @cog_ext.cog_slash(name="user", guild_ids=eval(environ["GUILDS"]))
    async def get_user(self, ctx, username):
        (b, r) = await make_request("https://api.jikan.moe/v4/users/{}".format(username))
        if not b:
            return
        user = json.loads(r.content)["data"]
        (b, r) = await make_request("https://api.jikan.moe/v4/users/{}/statistics".format(username))
        if not b:
            return
        user = (user["username"], 
                {"Gender": user["gender"],
                 "Last online": datetime.strptime(user["last_online"], "%Y-%m-%dT%H:%M:%S%z") if user["last_online"] != None else None,
                 "Birthday": datetime.strptime(user["birthday"], "%Y-%m-%dT%H:%M:%S%z").date() if user["birthday"] != None else None,
                 "Joined": datetime.strptime(user["joined"], "%Y-%m-%dT%H:%M:%S%z").date() if user["joined"] != None else None,
                 "Location": user["location"]},
                user["url"],
                user["images"]["jpg"]["image_url"])
        anime = json.loads(r.content)["data"]["anime"]
        anime = {"Total entries": anime["total_entries"],
                 "Eps. watched": anime["episodes_watched"],
                 "Days watched": anime["days_watched"],
                 "Mean score": anime["mean_score"],
                 "Watching": anime["watching"],
                 "Completed": anime["completed"],
                 "On hold": anime["on_hold"],
                 "Dropped": anime["dropped"],
                 "Plan to Watch": anime["plan_to_watch"],
                 "Rewatched": anime["rewatched"]}
        manga = json.loads(r.content)["data"]["manga"]
        manga = {"Total entries": manga["total_entries"],
                 "Chaps. read": manga["chapters_read"],
                 "Vols. read": manga["volumes_read"],
                 "Days read": manga["days_read"],
                 "Mean score": manga["mean_score"],
                 "Reading": manga["reading"],
                 "Completed": manga["completed"],
                 "On hold": manga["on_hold"],
                 "Dropped": manga["dropped"],
                 "Plan to Read": manga["plan_to_read"],
                 "Reread": manga["reread"]}
        await self.get_user_embed(ctx, user, anime, manga)

def setup(bot: Bot):
    bot.add_cog(Embed(bot))