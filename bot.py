# This is new in the discord.py 2.0 update
#imports
from configparser import ConfigParser
import os
import discord
from discord import app_commands

import json  
import datetime as dt
import random
import math


#configuring bot
config = ConfigParser()
if not os.path.exists("config.cfg"):
    raise FileNotFoundError("Run ./setup.sh first")
config.read('config.cfg')
token = config['bot']['token']
guildId = config['bot']['guildId']


last_accessed_date = None
current_string = None

# setting up the bot
intents = discord.Intents.all() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def daily_quote():
    quote = "no quote available - QuoteBot"

    with open('quotes.json', 'r') as f:
        date = dt.datetime.now().strftime("%d/%m/%Y")
        data = json.load(f)
        print(date)
        print(data)
        if len(data["quotes"]) == 0:
            return quote
        elif (data["metaData"]["time"] == date):
            quote = data["metaData"]["currentQuote"]["quote"] + "   - " + data["metaData"]["currentQuote"]["auteur"]
        else:
            data["metaData"]["time"] = date
            data["metaData"]["currentQuote"] = data["quotes"][random.randrange(0, len(data["quotes"]), 1)]
            quote = data["metaData"]["currentQuote"]["quote"] + "   - " + data["metaData"]["currentQuote"]["auteur"]
            
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
    guild=discord.Object(id=guildId)
)
async def quote(interaction):
    await interaction.response.send_message(daily_quote())
    
@tree.command(
    name="add_quote",
    description="Add a new quote",
    guild=discord.Object(id=guildId)
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
    guild=discord.Object(id=guildId)
)
async def stats(interaction):
    with open('quotes.json', 'r') as f:
        data = json.load(f)
        totalQuotes = len(data["quotes"])
        leaderBoard = {}
        
        for quote in data["quotes"]:
            if quote["auteur"].find("&") != -1:
                auteurs = quote["auteur"].split(" & ")
                for a in auteurs:
                    if not a.lower() in leaderBoard:
                        leaderBoard[a.lower()] = 1
                    else:
                        leaderBoard[a.lower()] += 1
                continue
            if quote["auteur"].find(" en ") != -1:
                auteurs = quote["auteur"].split(" en ")
                for a in auteurs:
                    if not a.lower() in leaderBoard:
                        leaderBoard[a.lower()] = 1
                    else:
                        leaderBoard[a.lower()] += 1
                continue
            if not quote["auteur"].lower() in leaderBoard:
                leaderBoard[quote["auteur"].lower()] = 1
            else:
                leaderBoard[quote["auteur"].lower()]+= 1
         
        leaderBoard = dict(sorted(leaderBoard.items(),key=lambda x:x[1],reverse=True))
        totalAuthors = len(leaderBoard)
        colWidth = max(math.log(totalQuotes, 10), len("totalAuthors"))
        cols = 2
        rows = 2
        board1 = makeBoard(colWidth, cols, rows)
        board1 = setValueInBoard(board1, "totalQuotes", 0, 0, cols, colWidth)
        board1 = setValueInBoard(board1, f"{totalQuotes}", 1, 0, cols, colWidth)
        board1 = setValueInBoard(board1, "totalAuthors", 0, 1, cols, colWidth)
        board1 = setValueInBoard(board1, f"{totalAuthors}", 1, 1, cols, colWidth)
        #print(board1)
        
        colWidth = 12
        cols = 3
        rows = 1+len(leaderBoard)
        board2 = makeBoard(colWidth, cols, rows)
        board2 = setValueInBoard(board2, "place", 0, 0, cols, colWidth)
        board2 = setValueInBoard(board2, "auteur", 1, 0, cols, colWidth)
        board2 = setValueInBoard(board2, "quotes", 2, 0, cols, colWidth)
        i = 1
        for auteur in leaderBoard:
            board2 = setValueInBoard(board2, f"{i}", 0, i, cols, colWidth)
            board2 = setValueInBoard(board2, auteur, 1, i, cols, colWidth)
            board2 = setValueInBoard(board2, f"{leaderBoard[auteur]}", 2, i, cols, colWidth)
            i+=1
        #print(board2)
        await interaction.response.send_message(board1+board2)
    
def setValueInBoard(board, value, x, y, cols, colWidth):
    label = chr((x)+(y*cols)+ord('{'))
    for i in range(len(value), colWidth):
        value+=" "
    board = board.replace(label, value)
    return board
  
def makeBoard(colWidth, cols, rows):
    board = "```\n┌"
    for j in range(cols):
        for i in range(colWidth):
            board += "─"
        if not j == cols-1:
            board += "┬"
    board+= "┐\n"
    for i in range(rows):
        for j in range(cols):
            board += f"│{chr((j)+(i*cols)+ord('{'))}"
        board += "│\n"
        
        if not i == rows-1:           
            board += "├"
            for k in range(cols):
                for l in range(colWidth):
                    board += "─"
                if not k == cols-1:
                    board += "┼"
            board+= "┤\n"
        
    board+= "└"
    for j in range(cols):
        for i in range(colWidth):
            board += "─"
        if not j == cols-1:
            board += "┴"
    board+= "┘\n```"
    return board
    
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildId))
    print("Ready!")

def main():
    if not os.path.exists("quotes.json"):
        raise FileNotFoundError("Run setup.sh first")
    # run the bot
    client.run(token)


if __name__ == "__main__":
    main()