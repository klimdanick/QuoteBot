import datetime as dt
import json
import random
from zoneinfo import ZoneInfo
import csv

class Quote:
    def __init__(self, quote, author, date = None):
        self.quote = quote
        self.author = author
        self.date_added = date

class Word:
    def __init__(self, word, meaning):
        self.word = word
        self.meaning = meaning

class MetaData:
    def __init__(self, time, currentQuote, currentWord):
        self.time = time
        self.currentQuote = currentQuote
        self.currentWord = currentWord

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
            data_dict = {}
            
        self.quotes = [Quote(**quote) for quote in data_dict.get("quotes", [])]

        if data_dict.get("metaData"):
            meta_data_dict = data_dict.get("metaData")
            if meta_data_dict is not None:
                self.metaData = MetaData(
                    meta_data_dict.get("time"),
                    Quote(**meta_data_dict.get("currentQuote")),
                    Word(**meta_data_dict.get("currentWord")) if meta_data_dict.get("currentWord") else self.get_random_word()
                )
        else:
            self.metaData = None


    def save_data(self):
        current_quote_dict = None
        current_word_dict = None

        if self.metaData:
            if self.metaData and self.metaData.currentQuote is not None:
                current_quote_dict = {
                    "quote": self.metaData.currentQuote.quote,
                    "author": self.metaData.currentQuote.author
                }
            if self.metaData.currentWord is not None:
                current_word_dict = {
                    "word": self.metaData.currentWord.word,
                    "meaning": self.metaData.currentWord.meaning
                }

        with open(self.file_path, 'w') as f:
            json.dump({
                "quotes": [{"quote": quote.quote, "author": quote.author, "date": quote.date_added if quote.date_added is not None else None} for quote in self.quotes],
                "metaData": {
                    "time": self.metaData.time,
                    "currentQuote": current_quote_dict,
                    "currentWord": current_word_dict
                } if self.metaData else None
            }, f, indent=4)

    def quote_of_the_day(self):
        date = dt.datetime.now(tz=self.tz).strftime("%d/%m/%Y")

        if not self.quotes:
            return "no quote available - QuoteBot"

        if self.metaData and self.metaData.time == date:
            return f'{self.metaData.currentQuote.quote} - {self.metaData.currentQuote.author}'
        
        new_quote = random.choice(self.quotes)
        new_word = self.get_random_word()
        self.metaData = MetaData(date, new_quote, new_word)
        self.save_data()

        return f'{new_quote.quote} - {new_quote.author}'

    def word_of_the_day(self):
        date = dt.datetime.now(tz=self.tz).strftime("%d/%m/%Y")
        if self.metaData and self.metaData.time == date:
            return f'{self.metaData.currentWord.word} - {self.metaData.currentWord.meaning}'

        word = self.get_random_word()
        return f"{word.word} - {word.meaning}"

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
                leaderboard[author.lower().strip()] = leaderboard.get(author.lower().strip(), 0) + 1
        totalQuotes = len(self.quotes)
        totalAuthors = len(leaderboard.keys())

        #  Sort on values
        return dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)), totalAuthors, totalQuotes

    def get_random_word(self):
        with open('words.csv', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

        word, meaning = random.choice(rows)

        return Word(word, meaning)

# Usage
quote_book = QuoteBook('quotes.json')
quote = quote_book.quote_of_the_day()
quote_book.get_stats()
print(quote)
