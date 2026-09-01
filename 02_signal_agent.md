# Module 2: The Signal Agent

## What you're building

A program that reads closing prices and produces one number per candle,
between **-1.0** (strongly bearish) and **+1.0** (strongly bullish),
by combining three classic technical indicators:

- **RSI** (Relative Strength Index)
- **Bollinger Bands** (specifically, "%B")
- **MACD** (Moving Average Convergence Divergence)

This single number is called **D_tech**, and it's what the Strategic
Supervisor Agent (Module 5) will use as the "technical opinion" input to
its decision formula.

## Why these three indicators?

Each one looks at price from a different angle, so combining them gives a
more balanced opinion than trusting just one:

- **RSI** asks: *"has price been rising or falling too fast, too
  recently?"*
- **Bollinger %B** asks: *"is price unusually far from its own recent
  average, relative to how much it normally moves?"*
- **MACD** asks: *"is short-term momentum currently above or below
  longer-term momentum?"*

## A note on the code style here

Every indicator function you'll write returns a **list the same length**
as the input price list. Early candles that don't have enough history yet
(e.g. you can't compute a 20-day average on day 5) get a `None` in that
slot instead of a number. This keeps every list lined up by position
(index), which makes everything downstream much simpler to reason about,
even though it's not the most memory-efficient approach.

---

## PART A — Questions

**Question 1 — Simple Moving Average (SMA).**
Write `calculate_sma(values, period)`. For every position `i` in the list,
if there isn't yet `period` worth of history, put `None`. Otherwise,
average the last `period` values ending at `i` (inclusive).

**Question 2 — Standard Deviation.**
Write `calculate_std_dev(values, period)`, same shape as Question 1, but
computing the standard deviation of the last `period` values instead of
the average. (Recall: standard deviation = square root of the average
squared distance from the mean.)

**Question 3 — RSI.**
Write `calculate_rsi(closes, period=14)`. For each candle (once enough
history exists), look at the last `period` price changes. Split each
change into a "gain" (if positive) or a "loss" (if negative, stored as a
positive number). Average the gains, average the losses, then compute:
```
RS  = average_gain / average_loss
RSI = 100 - (100 / (1 + RS))
```
(If average_loss is 0, RSI = 100.)

**Question 4 — Exponential Moving Average (EMA).**
Write `calculate_ema(values, period)`. Unlike SMA, EMA is *recursive* -
each value depends on the previous EMA value:
- The very first EMA (at index `period - 1`) is just a plain average of
  the first `period` values.
- Every EMA after that is: `(current_value - previous_ema) * multiplier + previous_ema`,
  where `multiplier = 2 / (period + 1)`.

**Question 5 — Bollinger %B.**
Write `calculate_bollinger_percent_b(closes, period=20, num_std_dev=2)`
using your Question 1 and 2 functions:
```
upper_band = SMA + (num_std_dev * std_dev)
lower_band = SMA - (num_std_dev * std_dev)
%B = (close - lower_band) / (upper_band - lower_band)
```

**Question 6 — MACD Histogram.**
Write `calculate_macd_histogram(closes, fast_period=12, slow_period=26, signal_period=9)`
using your Question 4 function:
1. `macd_line` = fast EMA minus slow EMA (candle by candle)
2. `signal_line` = an EMA of the `macd_line` itself
3. `histogram` = `macd_line - signal_line`

(Tricky bit: `macd_line` starts with a run of `None`s before the slow EMA
kicks in. You'll need to run EMA only on the real numbers, then place the
results back at the correct positions.)

**Question 7 — Opinion conversion.**
Write three small functions that turn each indicator's raw value into an
opinion between -1 and +1:
- `rsi_to_opinion(rsi_value)`: RSI of 0 → +1.0, RSI of 100 → -1.0, straight
  line in between.
- `bollinger_to_opinion(percent_b_value)`: %B of 0 → +1.0, %B of 1 → -1.0.
- `macd_to_opinion(histogram_value)`: positive histogram → +1.0, negative
  → -1.0, exactly zero → 0.0.

All three should return `None` if given `None`.

**Question 8 — Combine everything.**
Write `generate_tech_opinions(candles)` that:
1. Pulls out the closing prices from the candle list
2. Runs all three indicators
3. Converts each to an opinion using Question 7's functions
4. Averages whichever opinions are available for each candle (ignoring
   `None`s) into one final `D_tech` value per candle
5. Returns the list of D_tech values

---

## PART B — Pseudocode

**Question 1 (SMA):**
```
function calculate_sma(values, period):
    result = empty list

    for i from 0 to length(values) - 1:
        if i < period - 1:
            result.append(None)
        else:
            window = values from (i - period + 1) to i, inclusive
            result.append(average of window)

    return result
```

**Question 2 (Std Dev):** same shape as SMA, but:
```
mean = average of window
variance = average of (value - mean)^2 for each value in window
std_dev = square root of variance
```

**Question 3 (RSI):**
```
function calculate_rsi(closes, period):
    result = list of None, same length as closes

    for i from period to length(closes) - 1:
        gains = empty list
        losses = empty list

        for j from (i - period + 1) to i:
            change = closes[j] - closes[j - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(absolute value of change)

        average_gain = average of gains
        average_loss = average of losses

        if average_loss == 0:
            rsi = 100
        else:
            rs = average_gain / average_loss
            rsi = 100 - (100 / (1 + rs))

        result[i] = rsi

    return result
```

**Question 4 (EMA):**
```
function calculate_ema(values, period):
    result = list of None, same length as values

    if not enough values for even one period:
        return result

    result[period - 1] = average of first `period` values
    multiplier = 2 / (period + 1)

    for i from period to length(values) - 1:
        result[i] = (values[i] - result[i-1]) * multiplier + result[i-1]

    return result
```

**Question 5 (Bollinger %B):**
```
function calculate_bollinger_percent_b(closes, period, num_std_dev):
    sma = calculate_sma(closes, period)
    std_dev = calculate_std_dev(closes, period)
    result = empty list

    for i from 0 to length(closes) - 1:
        if sma[i] is None or std_dev[i] is None:
            result.append(None)
        else:
            upper = sma[i] + num_std_dev * std_dev[i]
            lower = sma[i] - num_std_dev * std_dev[i]
            result.append((closes[i] - lower) / (upper - lower))

    return result
```

**Question 6 (MACD):**
```
function calculate_macd_histogram(closes, fast, slow, signal_period):
    fast_ema = calculate_ema(closes, fast)
    slow_ema = calculate_ema(closes, slow)

    macd_line = fast_ema[i] - slow_ema[i] for each i (None if either is None)

    # signal line = EMA of macd_line, but skip the leading None values first
    valid_values = only the non-None entries of macd_line
    signal_of_valid = calculate_ema(valid_values, signal_period)
    # place signal_of_valid back into a full-length list at the correct offset

    histogram = macd_line[i] - signal_line[i] for each i (None if either is None)

    return histogram
```

**Question 7 (Opinions):**
```
function rsi_to_opinion(rsi):
    if rsi is None: return None
    opinion = (50 - rsi) / 50
    clip opinion to between -1 and 1
    return opinion

function bollinger_to_opinion(percent_b):
    if percent_b is None: return None
    opinion = (0.5 - percent_b) * 2
    clip opinion to between -1 and 1
    return opinion

function macd_to_opinion(histogram):
    if histogram is None: return None
    if histogram > 0: return 1.0
    if histogram < 0: return -1.0
    return 0.0
```

**Question 8 (Combine):**
```
function generate_tech_opinions(candles):
    closes = the "close" value from every candle

    rsi_values = calculate_rsi(closes)
    percent_b_values = calculate_bollinger_percent_b(closes)
    macd_values = calculate_macd_histogram(closes)

    tech_opinions = empty list

    for i from 0 to length(closes) - 1:
        rsi_op = rsi_to_opinion(rsi_values[i])
        boll_op = bollinger_to_opinion(percent_b_values[i])
        macd_op = macd_to_opinion(macd_values[i])

        available = the non-None values among [rsi_op, boll_op, macd_op]

        if available is empty:
            tech_opinions.append(None)
        else:
            tech_opinions.append(average of available)

    return tech_opinions
```

---

## PART C — Full Beginner Code

The runnable file is at: `code/02_signal_agent.py`
It uses the longer test dataset at: `sample_data/sample_XAUUSD_D1_extended.csv`
(60 candles - Bollinger and MACD need more history than the 10-row
Module 1 sample provides.)

```python
def calculate_sma(values, period):
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
    result = [None] * len(values)
    if len(values) < period:
        return result

    first_average = sum(values[0:period]) / period
    result[period - 1] = first_average
    multiplier = 2 / (period + 1)

    for i in range(period, len(values)):
        previous_ema = result[i - 1]
        current_value = values[i]
        result[i] = (current_value - previous_ema) * multiplier + previous_ema

    return result


def calculate_rsi(closes, period=14):
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
    fast_ema = calculate_ema(closes, fast_period)
    slow_ema = calculate_ema(closes, slow_period)

    macd_line = []
    for i in range(len(closes)):
        if fast_ema[i] is None or slow_ema[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(fast_ema[i] - slow_ema[i])

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


def rsi_to_opinion(rsi_value):
    if rsi_value is None:
        return None
    opinion = (50 - rsi_value) / 50
    return max(-1.0, min(1.0, opinion))


def bollinger_to_opinion(percent_b_value):
    if percent_b_value is None:
        return None
    opinion = (0.5 - percent_b_value) * 2
    return max(-1.0, min(1.0, opinion))


def macd_to_opinion(histogram_value):
    if histogram_value is None:
        return None
    if histogram_value > 0:
        return 1.0
    elif histogram_value < 0:
        return -1.0
    else:
        return 0.0


def generate_tech_opinions(candles):
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
```

### Checking your understanding

1. Why do the first ~25 candles in the dataset end up with `D_tech = None`?
2. If RSI = 20 (oversold), is the opinion positive or negative? Why does
   that make sense?
3. Why does MACD need a *recursive* (EMA-based) calculation, while RSI
   and Bollinger Bands can be recalculated fresh at each candle using
   only a fixed window of recent data?
4. What happens to the final D_tech value if, say, MACD's opinion is
   `None` but RSI and Bollinger's aren't? (Check the code — this matters
   for how the Supervisor Agent behaves early in a dataset.)

---

**Next: Module 3 — The News Agent**, where we'll load a pre-computed daily
sentiment score and turn it into a simple `D_news` opinion, ready to be
combined with `D_tech` by the Strategic Supervisor.
