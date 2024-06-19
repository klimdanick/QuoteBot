from configparser import ConfigParser
import os
from pathlib import Path
import discord

from zoneinfo import ZoneInfo

from utils import dictToTable
from QuoteBook import Quote, QuoteBook


#configuring bot
config = ConfigParser()
if not os.path.exists("config.cfg"):
    raise FileNotFoundError("Run ./setup.sh first")
config.read('config.cfg')
TOKEN = config['bot']['token']
GUILD_ID = config['bot']['guildId']
TZ = ZoneInfo(config["bot"]["TimeZone"]) if config.has_option("bot", "TimeZone") else ZoneInfo("Europe/Amsterdam")

quotebook = QuoteBook(Path(Path.cwd(),"quotes.json"), TZ)


# if you don't want all intents you can do discord.Intents.default()
intents = discord.Intents.all() 
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(
    name="quote",
    description="The daily quote!",
    guild=discord.Object(id=GUILD_ID)
)
async def quote(interaction):
    await interaction.response.send_message(quotebook.quote_of_the_day())
    
@tree.command(
    name="add_quote",
    description="Add a new quote",
    guild=discord.Object(id=GUILD_ID)
)
async def addQuote(interaction, quote: str, author: str):
    quotebook.add_quote(Quote(quote, author))
    await interaction.response.send_message(f"added quote from {author}!")

@tree.command(
    name="stats",
    description="See quote stats",
    guild=discord.Object(id=GUILD_ID)
) 
async def stats(interaction):
    leaderboard, totalAutors, totalQuotes = quotebook.get_stats()
    file = dictToTable(leaderboard, ["place", "author", "amount"]) 
    await interaction.response.send_message(file=discord.File((file)))
    file = dictToTable({totalAutors: totalQuotes,}, ["totalAuthors","totalQuotes"], False)
    await interaction.channel.send(file=discord.File((file)))
    
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Ready!")
def main():
    if not os.path.exists("quotes.json"):
        raise FileNotFoundError("Run setup.sh first")
    client.run(TOKEN)


if __name__ == "__main__":
    main()