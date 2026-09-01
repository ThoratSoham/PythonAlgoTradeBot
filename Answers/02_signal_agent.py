"""
MEMATS - Module 2: Signal Agent
=================================
This file turns raw closing prices into a single "technical opinion"
number between -1.0 (strongly bearish/sell) and +1.0 (strongly
bullish/buy), using three classic indicators:

  - RSI (Relative Strength Index)
  - Bollinger Bands (%B)
  - MACD (Moving Average Convergence Divergence)

Each indicator is computed the simple, "recalculate from scratch each
time" way. This is NOT the fastest way to do it, but it's the EASIEST
to read and trust as a beginner - and speed doesn't matter here since
this all runs offline during training.

Every indicator function below returns a list that's the SAME LENGTH
as the input closes list. Wherever there isn't enough history yet to
calculate a value (e.g. you can't compute a 20-candle average on the
5th candle), we put `None` in that spot instead of a number. This way
every list always lines up with the same candle by position (index).
"""


# ---------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------

def calculate_sma(values, period):
    """
    Simple Moving Average: the plain average of the last `period` values.
    Returns a list the same length as `values`, with None where there
    isn't enough history yet.
    """
    result = []

    for i in range(len(values)):
        if i < period - 1:
            result.append(None)
        else:
            window = values[i - period + 1: i + 1]
            average = sum(window) / period
            result.append(average)

    return result


def calculate_std_dev(values, period):
    """
    Standard deviation of the last `period` values - a measure of how
    spread out (volatile) the recent prices have been.
    """
    result = []

    for i in range(len(values)):
        if i < period - 1:
            result.append(None)
        else:
            window = values[i - period + 1: i + 1]
            mean = sum(window) / period
            variance = sum((v - mean) ** 2 for v in window) / period
            result.append(variance ** 0.5)

    return result


def calculate_ema(values, period):
    """
    Exponential Moving Average. Unlike SMA, this gives more weight to
    recent prices. It's "recursive" - each EMA value depends on the
    previous EMA value, so we build it up step by step from the start.
    """
    result = [None] * len(values)

    if len(values) < period:
        return result

    # The very first EMA value is just a plain SMA of the first `period` values
    first_average = sum(values[0:period]) / period
    result[period - 1] = first_average

    multiplier = 2 / (period + 1)

    for i in range(period, len(values)):
        previous_ema = result[i - 1]
        current_value = values[i]
        result[i] = (current_value - previous_ema) * multiplier + previous_ema

    return result


# ---------------------------------------------------------------------
# The three indicators
# ---------------------------------------------------------------------

def calculate_rsi(closes, period=14):
    """
    RSI measures whether recent price movement has been mostly gains
    or mostly losses. Ranges from 0 to 100.
      - RSI above 70  -> considered "overbought" (may fall soon)
      - RSI below 30  -> considered "oversold"   (may rise soon)
    """
    result = [None] * len(closes)

    for i in range(period, len(closes)):
        gains = []
        losses = []

        for j in range(i - period + 1, i + 1):
            change = closes[j] - closes[j - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        average_gain = sum(gains) / period
        average_loss = sum(losses) / period

        if average_loss == 0:
            rsi = 100.0
        else:
            relative_strength = average_gain / average_loss
            rsi = 100 - (100 / (1 + relative_strength))

        result[i] = rsi

    return result


def calculate_bollinger_percent_b(closes, period=20, num_std_dev=2):
    """
    Bollinger %B tells you WHERE the current price sits relative to its
    own recent volatility band.
      - %B near 1.0 -> price is near the upper band (overbought)
      - %B near 0.0 -> price is near the lower band (oversold)
    """
    sma = calculate_sma(closes, period)
    std_dev = calculate_std_dev(closes, period)

    percent_b = []

    for i in range(len(closes)):
        if sma[i] is None or std_dev[i] is None:
            percent_b.append(None)
            continue

        upper_band = sma[i] + (num_std_dev * std_dev[i])
        lower_band = sma[i] - (num_std_dev * std_dev[i])
        band_width = upper_band - lower_band

        if band_width == 0:
            percent_b.append(0.5)
        else:
            percent_b.append((closes[i] - lower_band) / band_width)

    return percent_b


def calculate_macd_histogram(closes, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD compares a fast EMA to a slow EMA to spot momentum shifts.
      - Histogram above 0 -> bullish momentum (fast EMA above slow EMA)
      - Histogram below 0 -> bearish momentum
    """
    fast_ema = calculate_ema(closes, fast_period)
    slow_ema = calculate_ema(closes, slow_period)

    macd_line = []
    for i in range(len(closes)):
        if fast_ema[i] is None or slow_ema[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(fast_ema[i] - slow_ema[i])

    # The "signal line" is an EMA of the MACD line itself.
    # We first pull out only the real numbers (skip the None gap at the start),
    # run EMA on those, then place the results back at the correct positions.
    valid_values = [v for v in macd_line if v is not None]
    signal_of_valid = calculate_ema(valid_values, signal_period)

    signal_line = [None] * len(closes)
    first_valid_index = next(i for i, v in enumerate(macd_line) if v is not None)
    for offset, value in enumerate(signal_of_valid):
        signal_line[first_valid_index + offset] = value

    histogram = []
    for i in range(len(closes)):
        if macd_line[i] is None or signal_line[i] is None:
            histogram.append(None)
        else:
            histogram.append(macd_line[i] - signal_line[i])

    return histogram


# ---------------------------------------------------------------------
# Turning each indicator into an "opinion" between -1 and +1
# ---------------------------------------------------------------------

def rsi_to_opinion(rsi_value):
    """RSI of 0 -> +1.0 (very bullish). RSI of 100 -> -1.0 (very bearish)."""
    if rsi_value is None:
        return None
    opinion = (50 - rsi_value) / 50
    return max(-1.0, min(1.0, opinion))


def bollinger_to_opinion(percent_b_value):
    """%B of 0 (lower band) -> +1.0. %B of 1 (upper band) -> -1.0."""
    if percent_b_value is None:
        return None
    opinion = (0.5 - percent_b_value) * 2
    return max(-1.0, min(1.0, opinion))


def macd_to_opinion(histogram_value):
    """Simple rule: positive histogram -> +1.0, negative -> -1.0."""
    if histogram_value is None:
        return None
    if histogram_value > 0:
        return 1.0
    elif histogram_value < 0:
        return -1.0
    else:
        return 0.0


# ---------------------------------------------------------------------
# Putting it all together
# ---------------------------------------------------------------------

def generate_tech_opinions(candles):
    """
    Takes a list of candles (from Module 1's load_candles) and returns
    a list of "D_tech" opinions - one per candle, averaging RSI,
    Bollinger, and MACD opinions together. Returns None for candles
    where not enough history exists yet.
    """
    closes = [candle["close"] for candle in candles]

    rsi_values = calculate_rsi(closes, period=14)
    percent_b_values = calculate_bollinger_percent_b(closes, period=20, num_std_dev=2)
    macd_histogram_values = calculate_macd_histogram(closes, 12, 26, 9)

    tech_opinions = []

    for i in range(len(closes)):
        rsi_opinion = rsi_to_opinion(rsi_values[i])
        boll_opinion = bollinger_to_opinion(percent_b_values[i])
        macd_opinion = macd_to_opinion(macd_histogram_values[i])

        available = [op for op in [rsi_opinion, boll_opinion, macd_opinion] if op is not None]

        if len(available) == 0:
            tech_opinions.append(None)
        else:
            tech_opinions.append(sum(available) / len(available))

    return tech_opinions


if __name__ == "__main__":
    import csv

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

    filepath = "../sample_data/sample_XAUUSD_D1_extended.csv"
    candles = load_candles(filepath)

    tech_opinions = generate_tech_opinions(candles)

    print(f"Loaded {len(candles)} candles from {filepath}")
    print("\nLast 5 tech opinions (D_tech):")
    for candle, opinion in zip(candles[-5:], tech_opinions[-5:]):
        print(f"  {candle['date']}: {opinion}")
