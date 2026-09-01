# Module 3: The News Agent

## What you're building

A program that reads a pre-computed daily sentiment score (a single
number from -5.0 to +5.0, meant to represent "how positive or negative
was the news today") and turns it into a `D_news` opinion between -1 and
+1, matched up to every candle.

## Why is this so much simpler than Module 2?

Running real sentiment analysis (feeding news headlines into a model like
FinBERT or DeepSeek) is heavy work — too heavy for a low-end PC to do
live, on every tick, without lag. So MEMATS makes a deliberate design
choice: **that heavy work happens once a day, somewhere else** (a
separate offline script, or an API call you run yourself), and the result
gets saved as a tiny CSV file:

```
Date,SentimentScore
2024.01.01,-1.76
2024.01.02,-3.49
2024.01.03,1.51
```

This module's only job is to **read that file and use it** — no AI
models running here at all. That's the whole point: by the time trading
happens, sentiment is just a number lookup, which takes microseconds.

One wrinkle: your 1H and 15M candles will have dates that include a time,
like `"2024.01.01 08:00"`, but sentiment is only published once per *day*.
So we need a way to strip the time off and just keep the date part before
looking anything up.

---

## PART A — Questions

**Question 1.**
Write `load_sentiment_scores(filepath)` that reads a CSV file with
columns `Date, SentimentScore` and returns a **dictionary** mapping each
date (as text) to its score (as a `float`).

**Question 2.**
Write `extract_date_only(datetime_string)` that takes a string like
`"2024.01.01 08:00"` or just `"2024.01.01"` and returns only the date
part, `"2024.01.01"`, with no time attached.
(Hint: what character always separates a date from a time?)

**Question 3.**
Write `sentiment_score_to_opinion(score)` that converts a raw score
(ranging from -5.0 to +5.0) into an opinion between -1.0 and +1.0.
(Hint: what's the simplest math operation that maps -5→-1 and +5→+1?)

**Question 4.**
Write `get_news_opinion_for_date(sentiment_lookup, date_string)` that:
1. Extracts just the date part from `date_string` (Question 2)
2. Looks it up in `sentiment_lookup` (Question 1's dictionary)
3. If found, converts it to an opinion (Question 3) and returns it
4. If NOT found (e.g. a day with no news data), returns `0.0` — a
   neutral opinion — instead of crashing

**Question 5.**
Write `generate_news_opinions(candles, sentiment_lookup)` that loops
through every candle and builds a list of `D_news` opinions, one per
candle, using Question 4's function.

---

## PART B — Pseudocode

**Question 1:**
```
function load_sentiment_scores(filepath):
    sentiment_lookup = empty dictionary

    open filepath as a CSV with a header row
    for each row:
        date = row's Date column
        score = row's SentimentScore column, converted to a number
        sentiment_lookup[date] = score

    return sentiment_lookup
```

**Question 2:**
```
function extract_date_only(datetime_string):
    split datetime_string on the space character
    return the first piece
```

**Question 3:**
```
function sentiment_score_to_opinion(score):
    opinion = score / 5.0
    clip opinion to between -1.0 and 1.0
    return opinion
```

**Question 4:**
```
function get_news_opinion_for_date(sentiment_lookup, date_string):
    day_only = extract_date_only(date_string)

    if day_only exists as a key in sentiment_lookup:
        score = sentiment_lookup[day_only]
        return sentiment_score_to_opinion(score)
    else:
        return 0.0
```

**Question 5:**
```
function generate_news_opinions(candles, sentiment_lookup):
    news_opinions = empty list

    for each candle in candles:
        opinion = get_news_opinion_for_date(sentiment_lookup, candle's date)
        news_opinions.append(opinion)

    return news_opinions
```

---

## PART C — Full Beginner Code

The runnable file is at: `code/03_news_agent.py`
It uses: `sample_data/sample_XAUUSD_D1_extended.csv` and
`sample_data/sample_sentiment.csv`

```python
import csv


def load_sentiment_scores(filepath):
    sentiment_lookup = {}

    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = row["Date"]
            score = float(row["SentimentScore"])
            sentiment_lookup[date] = score

    return sentiment_lookup


def extract_date_only(datetime_string):
    return datetime_string.split(" ")[0]


def sentiment_score_to_opinion(score):
    opinion = score / 5.0
    return max(-1.0, min(1.0, opinion))


def get_news_opinion_for_date(sentiment_lookup, date_string):
    day_only = extract_date_only(date_string)

    if day_only in sentiment_lookup:
        score = sentiment_lookup[day_only]
        return sentiment_score_to_opinion(score)
    else:
        return 0.0


def generate_news_opinions(candles, sentiment_lookup):
    news_opinions = []

    for candle in candles:
        opinion = get_news_opinion_for_date(sentiment_lookup, candle["date"])
        news_opinions.append(opinion)

    return news_opinions
```

### Checking your understanding

1. Why does `get_news_opinion_for_date` return `0.0` (neutral) instead of
   crashing when a date isn't found, and why is that a safer default than,
   say, returning `+1.0`?
2. If a 15-minute candle's date is `"2024.01.03 14:30"`, what value will
   `extract_date_only` return, and what will it be used for?
3. This module never looks at price at all — only dates. Why doesn't the
   News Agent need any candle data beyond each candle's date?
4. Later, in Module 10, we'll build a script that updates a *live* daily
   sentiment file every day. Based on what you've seen here, what do you
   think that script's output file needs to look like for this module's
   code to keep working without any changes?

---

**Next: Module 4 — The Trader/Risk Agent**, where we'll calculate
stop-loss, take-profit, trailing stops, and — critically — the lot size
math that keeps every trade risking exactly 3% of your capital.
