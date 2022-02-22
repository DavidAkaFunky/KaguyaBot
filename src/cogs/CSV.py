import discord, csv
from CSV_classes import AnimeData, MangaData
from discord.ext.commands import Cog, Bot
from time import sleep
from requests.exceptions import Timeout
from os import remove, environ
from discord_slash import cog_ext, SlashContext

class CSV (Cog):

    def __init__(self,bot):
        self.bot = bot

    def write_to_csv(self, data, csv_writer):
        csv_writer.writerow(data.get_header())
        for entry in data.table:
            csv_writer.writerow(data.get_element(entry)[0])

    @cog_ext.cog_slash(name="csv", guild_ids=eval(environ["GUILDS"]))
    async def csv(self, ctx: SlashContext, username, list_type):
        """Send anime or manga list via DM"""
        if list_type in ("a", "anime"):
            data = AnimeData()
        elif list_type in ("m", "manga"):
            data = MangaData()
        else:
            await ctx.send("Syntax: /csv [username] [type]\nFor anime, type = 'a' or 'anime'\nFor manga, type = 'm' or 'manga'", hidden = True)
            return
        filename = username + ".csv"
        with open(filename, "w", newline = "") as out:
            csv_writer = csv.writer(out, delimiter =";")
            await data.fetch_data(ctx, data, csv_writer, username)
            self.write_to_csv(data, csv_writer)
        with open(filename, "rb") as out:
            await ctx.send("Hey there! Here's your CSV file. If there's data missing, be sure to make it public on MAL!", file = discord.File(out, filename), hidden = True)
        remove(filename)
        with open("Graph.xlsx", "rb") as out:
            await ctx.send("Import your CSV file to this Excel file:", file = discord.File(out, "Graph.xlsx"), hidden = True)

def setup(bot: Bot):
    bot.add_cog(CSV(bot))