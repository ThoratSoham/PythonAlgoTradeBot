"""
MEMATS - Module 3: News Agent
================================
This file is much simpler than Module 2, on purpose. All the "heavy"
sentiment analysis (running DeepSeek/FinBERT on news text) is assumed
to have ALREADY happened somewhere else - offline, on a server or via
an API - and the result was saved as a simple CSV file:

    Date,SentimentScore
    2024.01.01,-1.76
    2024.01.02,-3.49
    ...

Each score ranges from -5.0 (very negative news) to +5.0 (very positive
news). This module's only job is to:
  1. Load that CSV into a lookup table (a dictionary)
  2. Convert each score into an opinion between -1 and +1
  3. Match each candle (even 1H or 15M candles) to the correct DAY's
     sentiment score, since sentiment is only updated once per day
"""

import csv


def load_sentiment_scores(filepath):
    """
    Reads a CSV file with columns Date, SentimentScore and returns a
    dictionary mapping date (as text, e.g. "2024.01.01") to the score
    (as a float).
    """
    sentiment_lookup = {}

    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = row["Date"]
            score = float(row["SentimentScore"])
            sentiment_lookup[date] = score

    return sentiment_lookup


def extract_date_only(datetime_string):
    """
    Candle dates might be a plain date ("2024.01.01") or a date plus a
    time ("2024.01.01 08:00", for 1H/15M candles). Sentiment is only
    published once per DAY, so we need just the date part to look it up.

    This just splits on the first space and keeps the part before it.
    """
    return datetime_string.split(" ")[0]


def sentiment_score_to_opinion(score):
    """
    Converts a raw sentiment score (-5.0 to +5.0) into an opinion
    between -1.0 and +1.0, by simply dividing by 5.
    """
    opinion = score / 5.0
    return max(-1.0, min(1.0, opinion))


def get_news_opinion_for_date(sentiment_lookup, date_string):
    """
    Looks up the sentiment opinion for a given candle's date.
    If we have no sentiment data for that day (e.g. a weekend, or a gap
    in the data), we default to 0.0 - a neutral opinion - rather than
    guessing or crashing.
    """
    day_only = extract_date_only(date_string)

    if day_only in sentiment_lookup:
        score = sentiment_lookup[day_only]
        return sentiment_score_to_opinion(score)
    else:
        return 0.0


def generate_news_opinions(candles, sentiment_lookup):
    """
    Takes a list of candles and the sentiment lookup table, and returns
    a list of D_news opinions - one per candle, in the same order.
    """
    news_opinions = []

    for candle in candles:
        opinion = get_news_opinion_for_date(sentiment_lookup, candle["date"])
        news_opinions.append(opinion)

    return news_opinions


if __name__ == "__main__":
    def load_candles(filepath):
        candles = []
        with open(filepath, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                candles.append({
                    "date": row["Date"],
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                })
        return candles

    candles_filepath = "../sample_data/sample_XAUUSD_D1_extended.csv"
    sentiment_filepath = "../sample_data/sample_sentiment.csv"

    candles = load_candles(candles_filepath)
    sentiment_lookup = load_sentiment_scores(sentiment_filepath)

    news_opinions = generate_news_opinions(candles, sentiment_lookup)

    print(f"Loaded {len(candles)} candles and {len(sentiment_lookup)} sentiment scores")
    print("\nFirst 5 candles and their news opinions (D_news):")
    for candle, opinion in zip(candles[:5], news_opinions[:5]):
        print(f"  {candle['date']}: {opinion}")
