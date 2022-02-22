import discord, csv, json
from CSV_classes import AnimeData, MangaData
from discord.ext.commands import Cog, Bot
from time import sleep
from requests.exceptions import Timeout
from os import remove, environ
from discord_slash import cog_ext, SlashContext

class Embed (Cog):

    def __init__(self,bot):
        self.bot = bot
    
    async def create_embed(self, ctx, msg, data, content, username, index, length):
        header = data.header
        entry = data.get_element(content[index])
        embed = discord.Embed(title = entry[0][0], color = data.status[content[index]["watching_status"]][1])
        for i in range(1, len(entry[0])):
            embed.add_field(name=data.header[i], value=entry[0][i] if entry[0][i] != "" else "N/A")
        embed.add_field(name="‎", value="[MyAnimeList link]({})".format(entry[1]), inline=False if i in (5,8) else True)
        embed.set_image(url=entry[2])
        embed.set_footer(text="{}'s {} list: Entry {} of {}".format(username.capitalize(), data.info["type"], index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed=embed)

    async def create_embed_list(self, ctx, data, content, username):
        def check(reaction, user):
            return str(reaction.emoji) in ["⬅", "➡"]         
        content = json.loads(content)["data"]
        embed = discord.Embed(title = "‎")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        index = 0
        length = len(content)
        while True:
            await self.create_embed(ctx, msg, data, content, username, index, length)
            reaction, user = await self.bot.wait_for('reaction_add')
            if str(reaction.emoji) == "➡":
                index = (index + 1) % length
                await msg.remove_reaction("➡", user)
            elif str(reaction.emoji) == "⬅":
                index = (index - 1) % length
                await msg.remove_reaction("⬅", user)

    async def fetch_data(self, ctx, data, username):
        for i in range(3):
            try:
                r = data.request(username)
                if r.status_code == 200:
                    await self.create_embed_list(ctx, data, r.content, username)
                    return True
                print ("The API returned an error (Attempt #{}). Code: {}".format(i+1, r.status_code))
            except Timeout:
                print ("The API didn't respond (Attempt #{}).".format(i+1))
            if i < 2:
                print ("Trying again...")
                sleep(1)
        await ctx.send("We couldn't fetch the data from the API. Please try again later!", hidden = True)
        return False

    @cog_ext.cog_slash(name="animelist", guild_ids=eval(environ["GUILDS"]))
    async def get_anime_list(self, ctx, username):
        """Send embed anime list"""
        await self.fetch_data(ctx, AnimeData(), username) 

def setup(bot: Bot):
    bot.add_cog(Embed(bot))