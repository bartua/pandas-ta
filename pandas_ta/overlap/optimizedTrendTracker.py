  
# -*- coding: utf-8 -*-
from numpy import NaN as npNaN
from pandas import DataFrame
from pandas_ta.overlap import hl2
from pandas_ta.overlap import vidya
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, verify_series


def ott(high, low, close, length=None,_shift=None, multiplier=None, **kwargs):
    """Indicator: Supertrend"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = int(length) if length and length > 0 else 7
    shift = int(_shift) if _shift and _shift > 0 else 0

    multiplier = float(multiplier) if multiplier and multiplier > 0 else 2.0
    
    # Calculate Results
    m = close.size
    dir_, trend, _ott = [0] * m, [0] * m, [0] * m
    # long, short = [npNaN] * m, [npNaN] * m

    MAvg = vidya(close,length)
    fark = MAvg*multiplier*0.01
    upperband = MAvg + fark
    lowerband = MAvg - fark

    for i in range(1, m):
        if MAvg.iloc[i] > upperband.iloc[i - 1]:
            dir_[i] = 1
        elif MAvg.iloc[i] < lowerband.iloc[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]
        
        if dir_[i] > 0:
            # lowerband.iloc[i] = lowerband.iloc[i]*(200+multiplier)/200
            trend[i] =  lowerband.iloc[i]
        else:
            # upperband.iloc[i] = upperband.iloc[i]*(200-multiplier)/200
            trend[i] = upperband.iloc[i]

        if MAvg.iloc[i]>trend[i]:
            _ott[i] = trend[i]*(200+multiplier)/200
        else:
            _ott[i] = trend[i]*(200-multiplier)/200 
    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
        f"OTTSL{_props}": MAvg,
        f"OTT{_props}": _ott,
        f"OTTd{_props}": dir_,
    }, index=close.index)

    df.name = f"OTT{_props}"
    df.category = "overlap"

    # Apply offset if needed
    df[f"OTT{_props}"] = df[f"OTT{_props}"].shift(shift)

    # Handle fills
    if 'fillna' in kwargs:
        df.fillna(kwargs['fillna'], inplace=True)

    if 'fill_method' in kwargs:
        df.fillna(method=kwargs['fill_method'], inplace=True)

    return df