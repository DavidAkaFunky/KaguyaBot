import discord, asyncio
from DataClasses import AnimeData, MangaData, User, Character
from discord.ext.commands import Cog, Bot
from os import environ
from discord_slash import cog_ext
from Requests import make_request

class Embed (Cog):

    def __init__(self, bot):
        self.bot = bot
        self.anime = AnimeData()
        self.manga = MangaData()
        self.user = User()
        self.character = Character()


    ########################## MISCELLANEOUS ##########################

    async def get_empty_embed(self, ctx, arrow_flag):
        embed = discord.Embed(title = "‎")
        msg = await ctx.send(embed = embed)
        if arrow_flag:
            await msg.add_reaction("⬅")
            await msg.add_reaction("➡")
        return msg

    async def get_arrow_reaction(self, msg, index, length):
        def check(reaction, user):
            return str(reaction.emoji) in ["⬅", "➡"] and reaction.message.id == msg.id and user != self.bot.user
        reaction, user = await self.bot.wait_for('reaction_add', check = check)
        if str(reaction.emoji) == "➡":
            index = (index + 1) % length
            await msg.remove_reaction("➡", user)
        elif str(reaction.emoji) == "⬅":
            index = (index - 1) % length
            await msg.remove_reaction("⬅", user)
        return index
    
    async def create_embed(self, title, data, url = None, colour = 0x26448f, image = None):
        embed = discord.Embed(title = title, color = colour)
        for key in data:
            embed.add_field(name = key, value = data[key])
        if url != None:
            embed.add_field(name = "‎", value = "[MyAnimeList link]({})".format(url), inline = False)
        if image != None:
            embed.set_image(url = image)
        return embed


    ########################## INDIVIDUAL ENTRY COMMANDS ##########################

    async def get_search_entry_embed(self, ctx, msg, data, content, name, index, length):
        entry = data.get_search_entry(content[index])
        embed = await self.create_embed(entry["Title"], entry["Data"], url = entry["URL"], colour = entry["Colour"], image = entry["Image"])
        embed.set_footer(text = "Search result {} of {}".format(index+1, length), icon_url = ctx.author.avatar_url)
        print(embed.to_dict())
        await msg.edit(embed = embed)

    async def get_search_embed(self, ctx, data, search, name):    
        msg = await self.get_empty_embed(ctx, True)
        index = 0
        length = len(search)
        while True:
            try:
                await self.get_search_entry_embed(ctx, msg, data, search, name, index, length)
                index = await self.get_arrow_reaction(msg, index, length)
            except asyncio.TimeoutError:
                break

    async def get_search(self, ctx, data, name):
        search = await data.fetch_search(ctx, name)
        if search != None:
            await self.get_search_embed(ctx, data, search, name)

    @cog_ext.cog_slash(name = "anime", guild_ids = eval(environ["GUILDS"]))
    async def get_anime(self, ctx, name):
        """Search for anime"""
        await self.get_search(ctx, self.anime, name)

    @cog_ext.cog_slash(name = "manga", guild_ids = eval(environ["GUILDS"]))
    async def get_manga(self, ctx, name):
        """Search for manga"""
        await self.get_search(ctx, self.manga, name)


    ########################## LIST COMMANDS ##########################

    async def get_list_entry_embed(self, ctx, msg, data, content, username, index, length):
        status = "watching_status" if "watching_status" in content[index] else "reading_status"
        entry = data.get_list_entry(content[index])
        embed = await self.create_embed(entry["Title"], entry["Data"], url = entry["URL"], colour = entry["Colour"], image = entry["Image"])
        embed.set_footer(text = "{}'s {} list: Entry {} of {}".format(username.capitalize(), data.get_info()["type"], index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed = embed)

    async def get_list_embed(self, ctx, data, content, username):
        msg = await self.get_empty_embed(ctx, True)
        index = 0
        length = len(content)
        while True:
            try:
                await self.get_list_entry_embed(ctx, msg, data, content, username, index, length)
                index = await self.get_arrow_reaction(msg, index, length)
            except asyncio.TimeoutError:
                break

    async def get_list(self, ctx, data, username):
        """Send username's list"""
        content = await data.fetch_list(ctx, username)
        if content != None:
            await self.get_list_embed(ctx, data, content, username)

    @cog_ext.cog_slash(name = "animelist", guild_ids = eval(environ["GUILDS"]))
    async def get_anime_list(self, ctx, username):
        """Send username's anime list"""
        await self.get_list(ctx, self.anime, username)

    @cog_ext.cog_slash(name = "mangalist", guild_ids = eval(environ["GUILDS"]))
    async def get_manga_list(self, ctx, username):
        """Show username's manga list"""
        await self.get_list(ctx, self.manga, username)
    

    ########################## CHARACTER COMMAND ##########################

    async def get_character_pic_embed(self, ctx, embed, msg, pics, index, length):
        embed.set_image(url = pics[index])
        embed.set_footer(text = "Image {} of {}".format(index+1, length), icon_url = ctx.author.avatar_url)
        await msg.edit(embed = embed)

    async def get_character_embed(self, ctx, msg, character):
        embed = await self.create_embed(character["Name"], character["Data"])
        embed.add_field(name = "About", value = character["About"], inline = False)
        embed.add_field(name = "‎", value = "[MyAnimeList link]({})".format(character["URL"]), inline = False)
        await msg.edit(embed = embed)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        index = 0
        pics = await self.character.get_images(ctx, character)
        length = len(pics)
        while True:
            try:
                await self.get_character_pic_embed(ctx, embed, msg, pics, index, length)
                index = await self.get_arrow_reaction(msg, index, length)
            except asyncio.TimeoutError:
                break

    async def get_character_list_embed(self, ctx, characters, length):
        def check(reaction, user):
            return reaction.emoji in emojis[:length] and reaction.message.id == msg.id and user != self.bot.user
        # This list is ugly but I don't know any better haha
        emojis = [u"\u0030" + u"\u20E3", u"\u0031" + u"\u20E3", u"\u0032" + u"\u20E3", u"\u0033" + u"\u20E3", u"\u0034" + u"\u20E3",
                  u"\u0035" + u"\u20E3", u"\u0036" + u"\u20E3", u"\u0037" + u"\u20E3", u"\u0038" + u"\u20E3", u"\u0039" + u"\u20E3"]
        embed = discord.Embed(title = "React with the number of the character of your choice:", color = 0x26448f)
        for i in range(length):
            embed.add_field(name = "Option {}".format(i), value = characters[i]["name"], inline = False)
        embed.set_footer(text = "If you can't find the character you want, try a more specific search!", icon_url = ctx.author.avatar_url)
        msg = await ctx.send(embed = embed)
        for i in range(length):
            await msg.add_reaction(emojis[i])
        reaction, user = await self.bot.wait_for('reaction_add', check = check)
        await msg.clear_reactions()
        return msg, emojis.index(reaction.emoji)

    @cog_ext.cog_slash(name = "character", guild_ids = eval(environ["GUILDS"]))
    async def get_character_list(self, ctx, name):
        """Search for anime/manga character"""
        characters = await make_request(ctx, "https://api.jikan.moe/v4/characters?q={}&order_by=favorites&sort=desc".format(name))
        if characters == None:
            return
        length = min(10, len(characters))
        if length == 0: # No character found
            return
        elif length == 1: # Only one character found: Show it directly
            msg = await self.get_empty_embed(ctx, False)
            character = characters[0]
        else: # More than a character found: Show 10 most popular, ask to choose via reaction
            msg, index = await self.get_character_list_embed(ctx, characters[:length], length)
            character = characters[index]
        await self.get_character_embed(ctx, msg, await self.character.get_character_data(character))


    ########################## USER COMMAND ##########################

    async def get_user_page_embed(self, ctx, msg, user, anime, manga, index, length):
        data = (user, anime, manga)
        options = ["user info", "anime data", "manga data"]
        entry = data[index]
        embed = await self.create_embed("{}'s {}".format(user["Name"], options[index]), entry["Data"], url = user["URL"], colour = user["Colour"], image = user["Image"])
        embed.set_footer(text = "Click left for {}\nClick right for {}".format(options[(index-1)%length], options[(index+1)%length]), icon_url = ctx.author.avatar_url)
        await msg.edit(embed = embed)

    async def get_user_embed(self, ctx, user, anime, manga):    
        msg = await self.get_empty_embed(ctx, True)
        index = 0
        length = 3
        while True:
            try:
                await self.get_user_page_embed(ctx, msg, user, anime, manga, index, length)
                index = await self.get_arrow_reaction(msg, index, length)
            except asyncio.TimeoutError:
                break

    @cog_ext.cog_slash(name = "user", guild_ids = eval(environ["GUILDS"]))
    async def get_user(self, ctx, username):
        user = await make_request(ctx, "https://api.jikan.moe/v4/users/{}".format(username))
        if user in (None, []):
            return
        user_data = await make_request(ctx, "https://api.jikan.moe/v4/users/{}/statistics".format(username))
        if user_data != None:
            await self.get_user_embed(ctx,
                                      self.user.get_user_data(user),
                                      self.anime.get_stats(user_data["anime"]),
                                      self.manga.get_stats(user_data["manga"]))

def setup(bot: Bot):
    bot.add_cog(Embed(bot))