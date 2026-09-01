# Module 1: The Data Pipeline

## What you're building

A small program that:
1. Reads candle data (Date, Open, High, Low, Close) from a CSV file.
2. Turns each candle into 5 "relative" numbers instead of raw prices.

## Why this matters (read this before starting)

A raw price like `2350.25` doesn't mean much on its own to a computer — the
number `2350` could be from a calm market or a crazy one, and it looks the
same either way. But a **percentage change**, like "the price moved up
0.4% since the last candle," means roughly the same thing no matter what
year or price level you're looking at. This is called making data
**stationary**, and it's the foundation everything else in MEMATS is built
on.

We'll compute 5 of these relative numbers for every candle:

| Name | Formula | In plain English |
|---|---|---|
| x1: Close-to-Close Return | (close_now − close_prev) / close_prev | Did price close higher or lower than last time? |
| x2: High-to-High Return | (high_now − high_prev) / high_prev | Did the candle's peak move up or down? |
| x3: Low-to-Low Return | (low_now − low_prev) / low_prev | Did the candle's bottom move up or down? |
| x4: High-to-Close Ratio | (high_now − close_now) / close_now | How long is the upper "wick" (rejection from highs)? |
| x5: Close-to-Low Ratio | (close_now − low_now) / close_now | How long is the lower "wick" (rejection from lows)? |

The first candle in any dataset gets **skipped** — there's no "previous
candle" to compare it against yet.

---

## PART A — Questions

Try to solve these yourself first. Don't scroll down until you've actually
attempted each one — that's where the learning happens.

**Question 1.**
Write a function `load_candles(filepath)` that:
- Opens a CSV file with columns `Date, Open, High, Low, Close`
- Reads every row
- Returns a **list of dictionaries**, one per candle, where the numeric
  columns (`Open`, `High`, `Low`, `Close`) are converted from text to
  actual numbers (`float`).

**Question 2.**
Write a function `calculate_ratios_for_one_candle(previous_candle, current_candle)`
that takes two candle dictionaries and returns a new dictionary containing
the 5 ratios (x1 through x5) for the **current** candle, using the formulas
in the table above.

**Question 3.**
Write a function `calculate_ratios(candles)` that:
- Takes the full list of candles (from Question 1)
- Loops through them starting from the **second** candle (index 1, not 0)
- Calls your Question 2 function on each consecutive pair
- Returns a list of all the ratio dictionaries

**Question 4.**
Put it all together: load a real CSV file, calculate the ratios for every
candle, and print the first 5 results to check they look reasonable.

---

## PART B — Pseudocode

Only look at this if you're stuck on a question above, or want to check
your approach before writing real code.

**For Question 1:**
```
function load_candles(filepath):
    create an empty list called candles

    open the file at filepath
    read it as a CSV with a header row

    for each row in the file:
        make a dictionary with:
            date  = the row's Date column (keep as text)
            open  = the row's Open column, converted to a number
            high  = the row's High column, converted to a number
            low   = the row's Low column, converted to a number
            close = the row's Close column, converted to a number
        add this dictionary to the candles list

    return candles
```

**For Question 2:**
```
function calculate_ratios_for_one_candle(previous_candle, current_candle):
    x1 = (current_candle's close - previous_candle's close) / previous_candle's close
    x2 = (current_candle's high  - previous_candle's high)  / previous_candle's high
    x3 = (current_candle's low   - previous_candle's low)   / previous_candle's low
    x4 = (current_candle's high  - current_candle's close)  / current_candle's close
    x5 = (current_candle's close - current_candle's low)    / current_candle's close

    return a dictionary containing date, x1, x2, x3, x4, x5
```

**For Question 3:**
```
function calculate_ratios(candles):
    create an empty list called ratio_list

    # start at index 1 because index 0 has no "previous" candle
    for i from 1 to (length of candles - 1):
        previous_candle = candles[i - 1]
        current_candle  = candles[i]

        ratios = calculate_ratios_for_one_candle(previous_candle, current_candle)
        add ratios to ratio_list

    return ratio_list
```

**For Question 4:**
```
candles = load_candles("some_file.csv")
print how many candles were loaded

ratios = calculate_ratios(candles)
print how many ratio rows were produced

print the first 5 entries of ratios
```

---

## PART C — Full Beginner Code

This is the complete, working solution. Try not to jump here first —
you'll learn far more by writing your own version and only checking this
when you're stuck or want to compare.

The runnable file is at: `code/01_data_pipeline.py`
A small test dataset is provided at: `sample_data/sample_XAUUSD_D1.csv`

```python
import csv


def load_candles(filepath):
    """
    Reads a CSV file and returns a list of candles.
    Each candle is a dictionary like:
        {"date": "2024.01.01", "open": 2050.0, "high": 2055.0,
         "low": 2045.0, "close": 2052.0}
    """
    candles = []

    with open(filepath, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            candle = {
                "date": row["Date"],
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
            }
            candles.append(candle)

    return candles


def calculate_ratios_for_one_candle(previous_candle, current_candle):
    """
    Returns a dictionary with the 5 relative ratios for the CURRENT candle.
    """
    prev_close = previous_candle["close"]
    prev_high = previous_candle["high"]
    prev_low = previous_candle["low"]

    curr_high = current_candle["high"]
    curr_low = current_candle["low"]
    curr_close = current_candle["close"]

    x1 = (curr_close - prev_close) / prev_close
    x2 = (curr_high - prev_high) / prev_high
    x3 = (curr_low - prev_low) / prev_low
    x4 = (curr_high - curr_close) / curr_close
    x5 = (curr_close - curr_low) / curr_close

    return {
        "date": current_candle["date"],
        "x1_close_to_close": x1,
        "x2_high_to_high": x2,
        "x3_low_to_low": x3,
        "x4_high_to_close": x4,
        "x5_close_to_low": x5,
    }


def calculate_ratios(candles):
    """
    Loops through all candles and returns a list of ratio dictionaries.
    The first candle is skipped (no previous candle to compare to).
    """
    ratio_list = []

    for i in range(1, len(candles)):
        previous_candle = candles[i - 1]
        current_candle = candles[i]
        ratios = calculate_ratios_for_one_candle(previous_candle, current_candle)
        ratio_list.append(ratios)

    return ratio_list


if __name__ == "__main__":
    filepath = "../sample_data/sample_XAUUSD_D1.csv"

    candles = load_candles(filepath)
    print(f"Loaded {len(candles)} candles from {filepath}")

    ratios = calculate_ratios(candles)
    print(f"Calculated ratios for {len(ratios)} candles")

    print("\nFirst 5 ratio rows:")
    for row in ratios[:5]:
        print(row)
```

### Checking your understanding

Before moving to Module 2, make sure you can answer these (no code needed):

1. Why do we skip the first candle when calculating ratios?
2. If a candle's close is *higher* than the previous candle's close, will
   x1 be positive or negative?
3. If a candle has a long upper wick (price spiked up then came back down
   before closing), will x4 be a bigger or smaller number than a candle
   with almost no upper wick?
4. Why do we use *ratios* instead of just feeding raw Open/High/Low/Close
   prices straight into the system?

---

**Next: Module 2 — The Signal Agent**, where we'll use RSI, Bollinger
Bands, and MACD to turn these ratios (and standard indicators) into a
single "technical opinion" between -1 and +1.
