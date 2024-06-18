# This is new in the discord.py 2.0 update
#imports
from configparser import ConfigParser
import os
import discord

import json  
import datetime as dt
import random
from zoneinfo import ZoneInfo

from stats import getStats, dictToTable


#configuring bot
config = ConfigParser()
if not os.path.exists("config.cfg"):
    raise FileNotFoundError("Run ./setup.sh first")
config.read('config.cfg')
TOKEN = config['bot']['token']
GUILD_ID = config['bot']['guildId']
TZ = ZoneInfo(config["bot"]["TimeZone"]) if config.has_option("bot", "TimeZone") else ZoneInfo("Europe/Amsterdam") 

last_accessed_date = None
current_string = None

# setting up the bot
intents = discord.Intents.all() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def daily_quote():
    with open('quotes.json', 'r') as f:
        date = dt.datetime.now(tz=TZ).strftime("%d/%m/%Y")
        data = json.load(f)

        if len(data["quotes"]) == 0:
            quote = "no quote available - QuoteBot"
        elif (data["metaData"]["time"] == date):
            quote = f'{data["metaData"]["currentQuote"]["quote"]} - { data["metaData"]["currentQuote"]["auteur"]}'
        else:
            data["metaData"]["time"] = date
            newQuote = random.choice(data["quotes"])
            data["metaData"]["currentQuote"] = newQuote
            quote  = f'{newQuote["quote"]} - {newQuote["auteur"]}'
            
    with open('quotes.json', 'w') as f:
        json.dump(data, f)
    
    return quote

# Add the guild ids in which the slash command will appear.
# If it should be in all, remove the argument, but note that
# it will take some time (up to an hour) to register the
# command if it's for all guilds.
@tree.command(
    name="quote",
    description="The daily quote!",
    guild=discord.Object(id=GUILD_ID)
)
async def quote(interaction):
    await interaction.response.send_message(daily_quote())
    
@tree.command(
    name="add_quote",
    description="Add a new quote",
    guild=discord.Object(id=GUILD_ID)
)
async def addQuote(interaction, quote: str, auteur: str):
    quote_obj = {}
    quote_obj["quote"] = quote
    quote_obj["auteur"] = auteur
    with open('quotes.json', 'r') as f:
        data = json.load(f)
    with open('quotes.json', 'w') as f:
        data["quotes"].append(quote_obj)
        json.dump(data, f)
    
    await interaction.response.send_message(f"added quote from {auteur}!")

@tree.command(
    name="stats",
    description="See quote stats",
    guild=discord.Object(id=GUILD_ID)
) 
async def stats(interaction):
    leaderboard, totalAutors, totalQuotes = getStats()
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
    # run the bot
    client.run(TOKEN)


if __name__ == "__main__":
    main()