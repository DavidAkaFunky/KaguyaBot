import discord, csv
from Data_classes import AnimeData, MangaData
from discord.ext.commands import Cog, Bot
from os import remove, environ
from discord_slash import cog_ext, SlashContext

class CSV (Cog):

    def __init__(self,bot):
        self.bot = bot
        self.anime = AnimeData()
        self.manga = MangaData()

    def write_to_csv(self, data, content, csv_writer):
        csv_writer.writerow(data.get_header())
        for entry in content:
            csv_writer.writerow(data.get_csv_line(entry))

    async def get_csv(self, ctx, username, data):
        filename = username + ".csv"
        with open(filename, "w", newline = "") as out:
            csv_writer = csv.writer(out, delimiter  = ";")
            content = await data.fetch_list(username)
            if content != None:
                self.write_to_csv(data, content, csv_writer)
        with open(filename, "rb") as out:
            await ctx.send("Hey there! Here's your CSV file. If there's data missing, be sure to make it public on MAL!", file = discord.File(out, filename), hidden = True)
        remove(filename)
        with open("Graph.xlsx", "rb") as out:
            await ctx.send("Import your CSV file to this Excel file:", file = discord.File(out, "Graph.xlsx"), hidden = True)

    @cog_ext.cog_slash(name = "animecsv", guild_ids = eval(environ["GUILDS"]))
    async def get_anime_csv(self, ctx, username):
        await self.get_csv(ctx, username, self.anime)

    @cog_ext.cog_slash(name = "mangacsv", guild_ids = eval(environ["GUILDS"]))
    async def get_manga_csv(self, ctx, username):
        await self.get_csv(ctx, username, self.manga)

def setup(bot: Bot):
    bot.add_cog(CSV(bot))