import discord

async def get_empty_embed(ctx, arrow_flag):
    embed = discord.Embed(title = "‎")
    msg = await ctx.send(embed = embed)
    if arrow_flag:
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
    return msg

async def get_arrow_reaction(msg, index, length, bot):
    def check(reaction, user):
        return str(reaction.emoji) in ["⬅", "➡"] and reaction.message.id == msg.id and user != bot.user
    reaction, user = await bot.wait_for('reaction_add', check = check)
    if str(reaction.emoji) == "➡":
        index = (index + 1) % length
        await msg.remove_reaction("➡", user)
    elif str(reaction.emoji) == "⬅":
        index = (index - 1) % length
        await msg.remove_reaction("⬅", user)
    return index

async def create_embed(title, data, url = None, image = None, footer = None, colour = 0x26448f):
    embed = discord.Embed(title = title, color = colour)
    for key in data:
        embed.add_field(name = key, value = data[key])
    if url != None:
        embed.add_field(name = "‎", value = footer, inline = False)
    if image != None:
        embed.set_image(url = image)
    return embed