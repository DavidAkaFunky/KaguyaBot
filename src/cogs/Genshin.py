import discord
from discord.ext.commands import Cog, Bot
from os import environ
from discord_slash import cog_ext

class Genshin (Cog):

    def __init__(self, bot):
        self.bot = bot

def setup(bot: Bot):
    bot.add_cog(Genshin(bot))