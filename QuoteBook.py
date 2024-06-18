import datetime as dt
import json
import random
from zoneinfo import ZoneInfo

class Quote:
    def __init__(self, quote, author, date = None):
        self.quote = quote
        self.author = author
        self.date_added = date

class MetaData:
    def __init__(self, time, currentQuote):
        self.time = time
        self.currentQuote = currentQuote

class QuoteBook:
    def __init__(self, file_path, tz=ZoneInfo("Europe/Amsterdam")):
        self.file_path = file_path
        self.tz = tz
        self.load_data()
        
    def load_data(self):
        try:
            with open(self.file_path, 'r') as f:
                data_dict = json.load(f)
        except FileNotFoundError:
            print("run setup.sh")
    
        self.quotes = [Quote(**quote) for quote in data_dict.get("quotes", [])]

        if data_dict.get("metaData"):
            meta_data_dict = data_dict.get("metaData")
            if meta_data_dict is not None:
                self.metaData = MetaData(meta_data_dict.get("time"), Quote(**meta_data_dict.get("currentQuote")))
        else:
            self.metaData = None


    def save_data(self):
            current_quote_dict = None
            if self.metaData and self.metaData.currentQuote is not None:
                current_quote_dict = {
                    "quote": self.metaData.currentQuote.quote,
                    "author": self.metaData.currentQuote.author
                }
                
            with open(self.file_path, 'w') as f:
                json.dump({
                    "quotes": [{"quote": quote.quote, "author": quote.author, "date": quote.date_added if quote.date_added is not None else None} for quote in self.quotes],
                    "metaData": {
                        "time": self.metaData.time,
                        "currentQuote": current_quote_dict
                    } if self.metaData else None
                }, f, indent=4)


    def quote_of_the_day(self):
        date = dt.datetime.now(tz=self.tz).strftime("%d/%m/%Y")

        if not self.quotes:
            return "no quote available - QuoteBot"

        if self.metaData and self.metaData.time == date:
            return f'{self.metaData.currentQuote.quote} - {self.metaData.currentQuote.author}'
        
        new_quote = random.choice(self.quotes)
        self.metaData = MetaData(date, new_quote)
        self.save_data()

        return f'{new_quote.quote} - {new_quote.author}'
    
    def add_quote(self, quote: Quote):
        quote.date_added =  dt.datetime.now(tz=self.tz).strftime("%d/%m/%Y")
        self.quotes.append(quote)
        self.save_data()
    
    def get_stats(self):
        leaderboard = {}
        for quote in self.quotes:
            for author in (
                quote.author.split("&")
                if "&" in quote.author
                else quote.author.split(" en ")
                if " en " in quote.author
                else [quote.author]
            ):
                leaderboard[author.lower()] = leaderboard.get(author.lower(), 0) + 1
        totalQuotes = len(self.quotes)
        totalAuthors = len(leaderboard.keys())

        #  Sort on values
        return dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)), totalAuthors, totalQuotes


# Usage
quote_book = QuoteBook('quotes.json')
quote = quote_book.quote_of_the_day()
quote_book.get_stats()
print(quote)
