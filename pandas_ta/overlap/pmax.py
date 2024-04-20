# -*- coding: utf-8 -*-
from numpy import NaN as npNaN
from pandas import DataFrame
from pandas_ta.overlap import hl2
from pandas_ta.overlap import ma
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, verify_series


def pmax(high, low, close, length=None, multiplier=None, mamode=None,offset=None, **kwargs):
    """Indicator: PMAX"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 10
    mamode = mamode.lower() if mamode and isinstance(mamode, str) else "ema"
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 3.0
    
    high = verify_series(high, length)
    low = verify_series(low, length)
    close = verify_series(close, length)
    offset = get_offset(offset)

    if high is None or low is None or close is None: return

    # Calculate Results
    
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [npNaN] * m, [npNaN] * m

    hl2_ = hl2(high, low)
    mavg = ma(mamode,hl2_,length=length)
    matr = multiplier * atr(high, low, close, length)
    upperband = mavg + matr
    lowerband = mavg - matr

    for i in range(1, m):
        if mavg.iloc[i] > upperband.iloc[i - 1]:
            dir_[i] = 1
        elif mavg.iloc[i] < lowerband.iloc[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lowerband.iloc[i]
        else:
            trend[i] = short[i] = upperband.iloc[i]

    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
            f"PMAX{_props}": trend,
            f"PMAXd{_props}": dir_,
            f"PMAXSL{_props}" : mavg,
            f"PMAXlong{_props}" : long,
            f"PMAXshort{_props}": short
        }, index=close.index)

    df.name = f"PMAX{_props}"
    df.category = "overlap"

    # Apply offset if needed
    if offset != 0:
        df = df.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    if "fill_method" in kwargs:
        df.fillna(method=kwargs["fill_method"], inplace=True)

    return df


pmax.__doc__ = \
"""PMAX (PMAX)

PMax is a brand new indicator developed by KivancOzbilgic in earlier 2020.

It's a combination of two trailing stop loss indicators;
One is Anıl Özekşi's MOST (Moving Stop Loss) Indicator
and the other one is well known ATR based SuperTrend.

Both MOST and SuperTrend Indicators are very good at trend following systems but conversely their performance is not bright in sideways market conditions like most of the other indicators.

Profit Maximizer - PMax tries to solve this problem. PMax combines the powerful sides of MOST (Moving Average Trend Changer) and SuperTrend (ATR price detection) in one indicator.

Backtest and optimization results of PMax are far better when compared to its ancestors MOST and SuperTrend. It reduces the number of false signals in sideways and give more reliable trade signals.

PMax is easy to determine the trend and can be used in any type of markets and instruments. It does not repaint.

The first parameter in the PMax indicator set by the three parameters is the period/length of ATR.

The second Parameter is the Multiplier of ATR which would be useful to set the value of distance from the built in Moving Average.

I personally think the most important parameter is the Moving Average Length and type.

PMax will be much sensitive to trend movements if Moving Average Length is smaller. And vice versa, will be less sensitive when it is longer.

As the period increases it will become less sensitive to little trends and price actions.

In this way, your choice of period, will be closely related to which of the sort of trends you are interested in.

We are under the effect of the uptrend in cases where the Moving Average is above PMax;
conversely under the influence of a downward trend, when the Moving Average is below PMax.

Returns:
    pd.DataFrame: PMAX (trend), PMAXd (direction), PMAXlong (long), PMAXshort (short) columns.
"""
