"""
MEMATS - Module 1: Data Pipeline
==================================
This file reads raw candlestick price data (Date, Open, High, Low, Close)
from a CSV file, and turns it into 5 "relative" numbers per candle.

WHY DO WE DO THIS?
-------------------
Raw prices (like "2350.25") don't tell a computer much on their own.
A gold price of 2350 in 2018 and a price of 2350 in 2024 might mean
completely different things, depending on what the market was doing
at the time. But a PERCENTAGE CHANGE (like "+0.4%") means roughly the
same thing no matter what year it is. This is called making the data
"stationary" - it behaves consistently over time, which makes it much
easier for our evolutionary agents to learn general patterns instead
of memorizing specific price levels.

We calculate 5 ratios for every candle (except the very first one,
since it has no previous candle to compare itself to):

1. Close-to-Close Return : how much did the close price move since
                            the last candle's close?
2. High-to-High Return   : how much did the high price move since
                            the last candle's high?
3. Low-to-Low Return     : how much did the low price move since
                            the last candle's low?
4. High-to-Close Ratio   : how big was the upper wick, relative to
                            where the candle closed?
5. Close-to-Low Ratio    : how big was the lower wick, relative to
                            where the candle closed?
"""

import csv


def load_candles(filepath):
    """
    Reads a CSV file and returns a list of candles.

    Each candle is a dictionary like:
        {"date": "2024.01.01", "open": 2050.0, "high": 2055.0,
         "low": 2045.0, "close": 2052.0}

    The CSV file is expected to have a header row with these columns:
        Date, Open, High, Low, Close
    (this is the standard format MT5 exports when you save chart data)
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
    Takes two candles (the previous one and the current one) and
    returns a dictionary with the 5 relative ratios for the
    CURRENT candle.
    """
    prev_close = previous_candle["close"]
    prev_high = previous_candle["high"]
    prev_low = previous_candle["low"]

    curr_high = current_candle["high"]
    curr_low = current_candle["low"]
    curr_close = current_candle["close"]

    # 1. Close-to-Close Return
    x1 = (curr_close - prev_close) / prev_close

    # 2. High-to-High Return
    x2 = (curr_high - prev_high) / prev_high

    # 3. Low-to-Low Return
    x3 = (curr_low - prev_low) / prev_low

    # 4. High-to-Close Ratio (size of the upper wick)
    x4 = (curr_high - curr_close) / curr_close

    # 5. Close-to-Low Ratio (size of the lower wick)
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
    Takes a list of candles and returns a list of ratio dictionaries.
    The first candle is skipped, since there's no "previous candle"
    to compare it to.
    """
    ratio_list = []

    for i in range(1, len(candles)):
        previous_candle = candles[i - 1]
        current_candle = candles[i]

        ratios = calculate_ratios_for_one_candle(previous_candle, current_candle)
        ratio_list.append(ratios)

    return ratio_list


if __name__ == "__main__":
    # ---- DEMO: point this at your own XAUUSD CSV file ----
    # A small sample file is provided in sample_data/ so you can test
    # this immediately without needing real MT5 exports yet.
    filepath = "../sample_data/sample_XAUUSD_D1.csv"

    candles = load_candles(filepath)
    print(f"Loaded {len(candles)} candles from {filepath}")

    ratios = calculate_ratios(candles)
    print(f"Calculated ratios for {len(ratios)} candles")

    print("\nFirst 5 ratio rows:")
    for row in ratios[:5]:
        print(row)
