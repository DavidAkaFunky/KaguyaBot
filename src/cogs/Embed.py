import discord, csv, json
from Data_classes import AnimeData, MangaData
from discord.ext.commands import Cog, Bot
from os import environ
from discord_slash import cog_ext
from Requests import make_request

class Embed (Cog):

    def __init__(self,bot):
        self.bot = bot
    
    async def create_search_entry_embed(self, ctx, msg, data, content, username, index, length):
        entry = data.get_entry(content[index])
        embed = discord.Embed(title = entry[0][0], color = 0x26448f if content[index]["status"].split()[0] == "Finished" else 0x2db039)
        for i in range(1, len(entry[0])):
            embed.add_field(name=data.get_search_header()[i], value=entry[0][i] if entry[0][i] != "" else "N/A")
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(entry[1]), inline=False if i in (4,7) else True)
        embed.set_image(url=entry[2])
        embed.set_footer(text="Search result {} of {}".format(index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def create_search_embed(self, ctx, data, username):
        def check(reaction, user):
            return str(reaction.emoji) in ["⬅", "➡"]         
        search = data.get_search()
        embed = discord.Embed(title = "‎")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        index = 0
        length = len(search)
        while True:
            await self.create_search_entry_embed(ctx, msg, data, search, username, index, length)
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            if str(reaction.emoji) == "➡":
                index = (index + 1) % length
                await msg.remove_reaction("➡", user)
            elif str(reaction.emoji) == "⬅":
                index = (index - 1) % length
                await msg.remove_reaction("⬅", user)

    async def get_search(self, ctx, data, name):
        if not data.fetch_search(name):
            await ctx.send("We couldn't fetch the data from the API. Please try again later!", hidden = True)
            return
        await self.create_search_embed(ctx, data, name)

    @cog_ext.cog_slash(name="manga", guild_ids=eval(environ["GUILDS"]))
    async def get_manga(self, ctx, name):
        """Search for manga"""
        await self.get_search(ctx, MangaData(), name)

    @cog_ext.cog_slash(name="anime", guild_ids=eval(environ["GUILDS"]))
    async def get_anime(self, ctx, name):
        """Search for anime"""
        await self.get_search(ctx, AnimeData(), name)

    async def create_list_entry_embed(self, ctx, msg, data, content, username, index, length):
        status = "watching_status" if "watching_status" in content[index] else "reading_status"
        entry = data.get_element(content[index])
        embed = discord.Embed(title = entry[0][0], color = data.get_status()[content[index][status]][1])
        for i in range(1, len(entry[0])):
            if status == "watching_status" and i == 7:
                continue
            embed.add_field(name=data.get_header()[i], value=entry[0][i] if entry[0][i] != "" else "N/A")
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(entry[1]), inline=False if i in (5,8) else True)
        embed.set_image(url=entry[2])
        embed.set_footer(text="{}'s {} list: Entry {} of {}".format(username.capitalize(), data.get_info()["type"], index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def create_list_embed(self, ctx, data, username):
        def check(reaction, user):
            return str(reaction.emoji) in ["⬅", "➡"]         
        table = data.get_table()
        embed = discord.Embed(title = "‎")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        index = 0
        length = len(table)
        while True:
            await self.create_list_entry_embed(ctx, msg, data, table, username, index, length)
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            if str(reaction.emoji) == "➡":
                index = (index + 1) % length
                await msg.remove_reaction("➡", user)
            elif str(reaction.emoji) == "⬅":
                index = (index - 1) % length
                await msg.remove_reaction("⬅", user)

    async def get_list(self, ctx, data, username):
        """Send embed anime list"""
        if not data.fetch_list(username):
            await ctx.send("We couldn't fetch the data from the API. Please try again later!", hidden = True)
            return
        await self.create_list_embed(ctx, data, username)

    @cog_ext.cog_slash(name="animelist", guild_ids=eval(environ["GUILDS"]))
    async def get_anime_list(self, ctx, username):
        """Send username's anime list"""
        await self.get_list(ctx, AnimeData(), username)

    @cog_ext.cog_slash(name="mangalist", guild_ids=eval(environ["GUILDS"]))
    async def get_manga_list(self, ctx, username):
        """Show username's manga list"""
        await self.get_list(ctx, MangaData(), username)
    

def setup(bot: Bot):
    bot.add_cog(Embed(bot))