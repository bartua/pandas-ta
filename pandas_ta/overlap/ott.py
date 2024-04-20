# -*- coding: utf-8 -*-
from numpy import NaN as npNaN
from pandas import DataFrame
from pandas_ta.overlap import ma
from pandas_ta.utils import get_offset, verify_series


def ott(close, length=None, multiplier=None,mamode=None, offset=None, **kwargs):
    """Indicator: Supertrend"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 5
    mamode = mamode.lower() if mamode and isinstance(mamode, str) else "vidya"
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 2.4
    close = verify_series(close, length)
    offset = get_offset(offset)

    if close is None: return
    # Calculate Results
    m = close.size
    dir_, trend, afterDir = [1] * m, [0] * m, [1] * m
    long, short = [npNaN] * m, [npNaN] * m
    mavg = ma(mamode,close,length=length)
    matr = multiplier * mavg * 0.01
    upperband = mavg + matr
    lowerband = mavg - matr 

    for i in range(1, m):
        if mavg.iloc[i] > upperband.iloc[i - 1]:
            dir_[i] = 1
        elif mavg.iloc[i] < lowerband.iloc[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:# and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:# and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]
        if dir_[i] > 0:
            trend[i] = lowerband.iloc[i]*(200+multiplier)/200
        else:
            trend[i] = upperband.iloc[i]*(200-multiplier)/200
    
    for i in range(1,m):
        if mavg.iloc[i]>trend[i-2]:
            afterDir[i] = 1
        elif mavg.iloc[i]<trend[i-1]:
            afterDir[i] = -1
        else:
            afterDir[i] = afterDir[i-1]

    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
            f"OTT{_props}": trend,
            f"OTTSL{_props}": mavg,
            f"OTTd{_props}": afterDir
            # f"OTTnewDir{_props}": afterDir,
            # f"OTTl{_props}": long,
            # f"OTTs{_props}": short,
        }, index=close.index)

    df.name = f"OTT{_props}"
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


ott.__doc__ = \
"""OTT (ott)
Args:
    close (pd.Series): Series of 'close's
    length (int) : length for Moving Average calculation. Default: 5
    multiplier (float): Percentage difference for upper and lower band distance to
        Moving Average. Default: 2.4
    offset (int): How many periods to offset the result. Default: 0
    mamode (str): Sets which moving average to use. Default: 'vidya'

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: OTT (trend), OTTd (direction), OTTl (long), OTTs (short) columns.
"""
