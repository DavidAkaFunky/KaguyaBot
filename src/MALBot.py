from os import environ
from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from discord_slash import SlashCommand

load_dotenv()

extensions = ["cogs.Events", "cogs.MAL", "cogs.Genshin"]

client = Bot(command_prefix = "k!", self_bot = True, intents = Intents.all())
slash = SlashCommand(client, sync_commands = True)

for ext in extensions:
    client.load_extension(ext)

# info = open("info.txt", "r")
# info = info.read().splitlines()
client.run(environ["BOT_TOKEN"])