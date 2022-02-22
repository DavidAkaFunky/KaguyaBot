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

    async def fetch_and_write_data(self, ctx, data, csv, username):
        for i in range(3):
            try:
                r = data.request(username)
                if r.status_code == 200:
                    data.write_to_csv(csv, r.content)
                    return True
                print ("The API returned an error (Attempt #{}). Code: {}".format(i+1, r.status_code))
            except Timeout:
                print ("The API didn't respond (Attempt #{}).".format(i+1))
            if i < 2:
                print ("Trying again...")
                sleep(1)
        await ctx.send("We couldn't fetch the data from the API. Please try again later!", hidden = True)
        return False

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
        out = open(filename, "w", newline = "")
        csv_writer = csv.writer(out, delimiter =";")
        ret = await self.fetch_and_write_data(ctx, data, csv_writer, username)
        if ret:
            with open(filename, "rb") as out:
                await ctx.send("Hey there! Here's your CSV file. If there's data missing, be sure to make it public on MAL!", file = discord.File(out, filename), hidden = True)
            remove(filename)
            with open("Graph.xlsx", "rb") as out:
                await ctx.send("Import your CSV file to this Excel file:", file = discord.File(out, "Graph.xlsx"), hidden = True)
        out.close()

def setup(bot: Bot):
    bot.add_cog(CSV(bot))