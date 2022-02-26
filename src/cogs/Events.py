from discord.ext import commands
from discord.ext.commands import CommandNotFound
import discord

class Events (commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Kaguya-sama wa Kokurasetai: Tensai-tachi no Renai Zunousen"))
        print("I've joined, my username is {0.user}!".format(self.bot))

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        """Show when the given command doesn't exist"""
        if isinstance(error,CommandNotFound):
            await ctx.send("Sorry, this command doesn't exist! :/")
        else:
            raise error

def setup(bot):
    bot.add_cog(Events(bot))