# -*- coding: utf-8 -*-
from numpy import NaN as npNaN
from pandas import DataFrame
from pandas_ta.overlap import sma
from pandas_ta.utils import get_offset, verify_series


def ssl(high, low, close, length=None, offset=None, **kwargs):
    """Indicator: SSL"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 10
    high = verify_series(high, length)
    low = verify_series(low, length)
    close = verify_series(close, length)
    offset = get_offset(offset)

    if high is None or low is None or close is None: return

    # Calculate Results
    m = close.size
    dir_ = [1] * m
    sslUp, sslDown = [npNaN] * m, [npNaN] * m

    upperband = sma(high,length)
    lowerband = sma(low,length)

    for i in range(1, m):
        if close.iloc[i] > upperband.iloc[i]:
            dir_[i] = 1
        elif close.iloc[i] < lowerband.iloc[i]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
        
        if dir_[i] > 0:
            sslUp[i] = lowerband.iloc[i]
            sslDown[i] = upperband.iloc[i]
        else:
            sslUp[i] = upperband.iloc[i]
            sslDown[i] = lowerband.iloc[i]

    # Prepare DataFrame to return
    _props = f"_{length}"
    df = DataFrame({
            f"SSLd{_props}": dir_,
            f"SSL_Up{_props}": sslUp,
            f"SSL_Dn{_props}": sslDown,
        }, index=close.index)

    df.name = f"SSL{_props}"
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


ssl.__doc__ = \
"""SSL
"""
