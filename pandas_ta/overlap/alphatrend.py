# -*- coding: utf-8 -*-
from numpy import NaN as npNaN
from pandas import DataFrame
from pandas import Series
from pandas_ta.overlap import hl2
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, verify_series
from pandas_ta.momentum import rsi as rsi_imported
from pandas_ta.volume import mfi as mfi_imported
# AP = input(14, 'Common Period')
# upT = low - ATR * coeff
# downT = high + ATR * coeff
# AlphaTrend = 0.0
# AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50) ?( upT < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT) : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

# color1 = AlphaTrend > AlphaTrend[2] ? #00E60F : AlphaTrend < AlphaTrend[2] ? #80000B : AlphaTrend[1] > AlphaTrend[3] ? #00E60F : #80000B
# k1 = plot(AlphaTrend, color=color.new(#0022FC, 0), linewidth=3)
# k2 = plot(AlphaTrend[2], color=color.new(#FC0400, 0), linewidth=3)

def alphatrend(high, low, close, volume,length=None, multiplier=None, offset=None,volumeCalculation = None, **kwargs):
    """Indicator: alphaTrend"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 14
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 1.0
    high = verify_series(high, length)
    low = verify_series(low, length)
    close = verify_series(close, length)
    volume = verify_series(volume, length)
    offset = get_offset(offset)
    volumeCalculation = bool(volumeCalculation) if volumeCalculation and isinstance(volumeCalculation, bool) else True

    if high is None or low is None or close is None: return

    # Calculate Results
    m = close.size
    dir_, trend = [0] * m, [0] * m
    alphaTrend = Series([0]*m)
    # alphaTrendOutcome = [0] * m
    
    selectedIndicator = None

    if volumeCalculation:
        selectedIndicator = mfi_imported(high, low, close, volume, length=length,talib=False)
    else:
        selectedIndicator = rsi_imported(close, length=length)
    # rsi = rsi(close, length=length)
    # mfi = mfi(high, low, close, volume, length=length)
    
    matr = multiplier * atr(high, low, close, length,mamode="sma")
    upperband = low - matr
    lowerband = high + matr
    
    for i in range(1, m):
        if selectedIndicator.iloc[i] >= 50:
            if upperband[i] < alphaTrend.iloc[i - 1]:
                alphaTrend.iloc[i] = alphaTrend.iloc[i - 1]
            else:
                alphaTrend.iloc[i] = upperband[i]
        else:
            if lowerband[i] > alphaTrend.iloc[i - 1]:
                alphaTrend.iloc[i] = alphaTrend.iloc[i - 1]
            else:
                alphaTrend.iloc[i] = lowerband[i]
        
    alphaTrendShifted = alphaTrend.shift(2)
    # dir_ equals to when alphaTrend>alphaTrend[2] then 1 else -1 fill until it changes
    for i in range(1, m):
        if alphaTrend.iloc[i] > alphaTrendShifted.iloc[i]:
            dir_[i] = 1
        elif alphaTrend.iloc[i] < alphaTrendShifted.iloc[i]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]



    # alphaTrendOutcome[i] = alphaTrend.iloc[i]

    # shift alphaTrendOutcome by 2

        # print("alphaTrend",alphaTrend[i])

    # for i in range(1, m):
    #     if close.iloc[i] > upperband.iloc[i - 1]:
    #         dir_[i] = 1
    #     elif close.iloc[i] < lowerband.iloc[i - 1]:
    #         dir_[i] = -1
    #     else:
    #         dir_[i] = dir_[i - 1]
    #         if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
    #             lowerband.iloc[i] = lowerband.iloc[i - 1]
    #         if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
    #             upperband.iloc[i] = upperband.iloc[i - 1]

    #     if dir_[i] > 0:
    #         trend[i] = long[i] = lowerband.iloc[i]
    #     else:
    #         trend[i] = short[i] = upperband.iloc[i]

    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
            f"alphaTrend{_props}": alphaTrend.to_list(),
            f"alphaTrendSignal{_props}": alphaTrend.shift(2).to_list(),
            f"alphaTrendDir{_props}": dir_
            # f"SUPERTl{_props}": long,
            # f"SUPERTs{_props}": short,
        }, index=close.index)

    df.name = f"alphaTrend{_props}"
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


alphatrend.__doc__ = \
"""Alphatrend (alphatrend)

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int) : length for ATR calculation. Default: 7
    multiplier (float): Coefficient for upper and lower band distance to
        midrange. Default: 3.0
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: SUPERT (trend), SUPERTd (direction), SUPERTl (long), SUPERTs (short) columns.
"""



# def ott(close, length=None, multiplier=None,mamode=None, offset=None, **kwargs):
#     """Indicator: Supertrend"""
#     # Validate Arguments
#     length = int(length) if length and length > 0 else 5
#     mamode = mamode.lower() if mamode and isinstance(mamode, str) else "vidya"
#     multiplier = float(multiplier) if multiplier and multiplier > 0 else 2.4
#     close = verify_series(close, length)
#     offset = get_offset(offset)

#     if close is None: return
#     # Calculate Results
#     m = close.size
#     dir_, trend, afterDir = [1] * m, [0] * m, [1] * m
#     long, short = [npNaN] * m, [npNaN] * m
#     mavg = ma(mamode,close,length=length)
#     matr = multiplier * mavg * 0.01
#     upperband = mavg + matr
#     lowerband = mavg - matr 

#     for i in range(1, m):
#         if mavg.iloc[i] > upperband.iloc[i - 1]:
#             dir_[i] = 1
#         elif mavg.iloc[i] < lowerband.iloc[i - 1]:
#             dir_[i] = -1
#         else:
#             dir_[i] = dir_[i - 1]
#             if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:# and lowerband.iloc[i] < lowerband.iloc[i - 1]:
#                 lowerband.iloc[i] = lowerband.iloc[i - 1]
#             if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:# and upperband.iloc[i] > upperband.iloc[i - 1]:
#                 upperband.iloc[i] = upperband.iloc[i - 1]
#         if dir_[i] > 0:
#             trend[i] = lowerband.iloc[i]*(200+multiplier)/200
#         else:
#             trend[i] = upperband.iloc[i]*(200-multiplier)/200
    
#     for i in range(1,m):
#         if mavg.iloc[i]>trend[i-2]:
#             afterDir[i] = 1
#         elif mavg.iloc[i]<trend[i-1]:
#             afterDir[i] = -1
#         else:
#             afterDir[i] = afterDir[i-1]

#     # Prepare DataFrame to return
#     _props = f"_{length}_{multiplier}"
#     df = DataFrame({
#             f"OTT{_props}": trend,
#             f"OTTSL{_props}": mavg,
#             f"OTTd{_props}": afterDir
#             # f"OTTnewDir{_props}": afterDir,
#             # f"OTTl{_props}": long,
#             # f"OTTs{_props}": short,
#         }, index=close.index)

#     df.name = f"OTT{_props}"
#     df.category = "overlap"

#     # Apply offset if needed
#     if offset != 0:
#         df = df.shift(offset)

#     # Handle fills
#     if "fillna" in kwargs:
#         df.fillna(kwargs["fillna"], inplace=True)

#     if "fill_method" in kwargs:
#         df.fillna(method=kwargs["fill_method"], inplace=True)

#     return df


# ott.__doc__ = \
# """OTT (ott)
# Args:
#     close (pd.Series): Series of 'close's
#     length (int) : length for Moving Average calculation. Default: 5
#     multiplier (float): Percentage difference for upper and lower band distance to
#         Moving Average. Default: 2.4
#     offset (int): How many periods to offset the result. Default: 0
#     mamode (str): Sets which moving average to use. Default: 'vidya'

# Kwargs:
#     fillna (value, optional): pd.DataFrame.fillna(value)
#     fill_method (value, optional): Type of fill method

# Returns:
#     pd.DataFrame: OTT (trend), OTTd (direction), OTTl (long), OTTs (short) columns.
# """
