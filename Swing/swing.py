import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from ta.utils import dropna

def get_DEMA(data, window):
    EMA = data.ewm(span=window, adjust=False).mean()
    DEMA = 2 * EMA - EMA.ewm(span=window, adjust=False).mean()
    return DEMA

# Define the symbols
symbols = ['ABB.NS', 'ADANIENSOL.NS', 'ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS', 'ATGL.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS', 'ASIANPAINT.NS', 'DMART.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BAJAJHLDNG.NS', 'BANKBARODA.NS', 'BERGEPAINT.NS', 'BEL.NS', 'BPCL.NS', 'BHARTIARTL.NS', 'BOSCHLTD.NS', 'BRITANNIA.NS', 'CANBK.NS', 'CHOLAFIN.NS', 'CIPLA.NS', 'COALINDIA.NS', 'COLPAL.NS', 'DLF.NS', 'DABUR.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GAIL.NS', 'GODREJCP.NS', 'GRASIM.NS', 'HCLTECH.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HAVELLS.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HAL.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'ITC.NS', 'IOC.NS', 'IRCTC.NS', 'IRFC.NS', 'INDUSINDBK.NS', 'NAUKRI.NS', 'INFY.NS', 'INDIGO.NS', 'JSWSTEEL.NS', 'JINDALSTEL.NS', 'JIOFIN.NS', 'KOTAKBANK.NS', 'LTIM.NS', 'LT.NS', 'LICI.NS', 'M&M.NS', 'MARICO.NS', 'MARUTI.NS', 'NTPC.NS', 'NESTLEIND.NS', 'ONGC.NS', 'PIDILITIND.NS', 'PFC.NS', 'POWERGRID.NS', 'PNB.NS', 'RECLTD.NS', 'RELIANCE.NS', 'SBICARD.NS', 'SBILIFE.NS', 'SRF.NS', 'MOTHERSON.NS', 'SHREECEM.NS', 'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SBIN.NS', 'SUNPHARMA.NS', 'TVSMOTOR.NS', 'TCS.NS', 'TATACONSUM.NS', 'TATAMTRDVR.NS', 'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS', 'TORNTPHARM.NS', 'TRENT.NS', 'ULTRACEMCO.NS', 'MCDOWELL-N.NS', 'VBL.NS', 'VEDL.NS', 'WIPRO.NS', 'ZOMATO.NS', 'ZYDUSLIFE.NS']

# Create empty dataframes to store buy and sell signals
buy_df = pd.DataFrame(columns=['Symbol', 'Date', 'Close'])
sell_df = pd.DataFrame(columns=['Symbol', 'Date', 'Close'])

for symbol in symbols:
    # Download stock data from Yahoo Finance
    stock = yf.Ticker(symbol)
    df = stock.history(period="max")

    # Ensure the dataframe does not contain NaN values
    df = dropna(df)

    # Calculate technical indicators
    sma50 = SMAIndicator(close=df['Close'], window=50)
    sma200 = SMAIndicator(close=df['Close'], window=200)
    rsi = RSIIndicator(close=df['Close'], window=14)

    df['SMA50'] = sma50.sma_indicator()
    df['SMA200'] = sma200.sma_indicator()
    df['RSI'] = rsi.rsi()

    # Calculate ZeroLag MACD
    EMAfast = get_DEMA(df['Close'], 12)
    EMAslow = get_DEMA(df['Close'], 26)
    MACD = EMAfast - EMAslow
    Signal = get_DEMA(MACD, 9)
    ZeroLagMACD = MACD - Signal

    df['ZeroLagMACD'] = ZeroLagMACD

    # Check if price crosses above/below moving averages
    df['CrossedAbove50'] = df['Close'].gt(df['SMA50']).diff().gt(0)
    df['CrossedBelow50'] = df['Close'].lt(df['SMA50']).diff().lt(0)
    df['CrossedAbove200'] = df['Close'].gt(df['SMA200']).diff().gt(0)
    df['CrossedBelow200'] = df['Close'].lt(df['SMA200']).diff().lt(0)

    # Identify support and resistance levels using pivot points
    def pivot_points(high, low, close):
        pivot = (high + low + close) / 3
        support = pivot - (high - low)
        resistance = pivot + (high - low)
        return support, resistance

    df['Support'], df['Resistance'] = pivot_points(df['High'], df['Low'], df['Close'])

    # Check if price is near support or resistance
    df['NearSupport'] = df['Close'].between(df['Support'] * 0.99, df['Support'] * 1.01)
    df['NearResistance'] = df['Close'].between(df['Resistance'] * 0.99, df['Resistance'] * 1.01)

    # Filter for stocks meeting swing trading criteria
    buy_signals = (
        df['CrossedAbove50'] & df['CrossedAbove200'] &
        df['NearSupport'] & (df['RSI'].shift(1) < 30) #&
        #(df['ZeroLagMACD'].shift(1) < 0) & (df['ZeroLagMACD'] > 0)  # ZeroLagMACD crosses above zero
    )
    sell_signals = (
        df['CrossedBelow50'] & df['CrossedBelow200'] &
        df['NearResistance'] & (df['RSI'].shift(1) > 70) #&
        #(df['ZeroLagMACD'].shift(1) > 0) & (df['ZeroLagMACD'] < 0)  # ZeroLagMACD crosses below zero
    )

    # Fill NaN values with False
    buy_signals = buy_signals.fillna(False)
    sell_signals = sell_signals.fillna(False)

    # Get dates with buy/sell signals
    buy_dates = df.loc[buy_signals.shift(1).fillna(False).infer_objects(), 'Close']
    sell_dates = df.loc[sell_signals.shift(1).fillna(False).infer_objects(), 'Close']


    # Append to buy and sell dataframes
    for date, close in buy_dates.items():
        buy_df = buy_df.append({'Symbol': symbol, 'Date': date, 'Close': close}, ignore_index=True)
    for date, close in sell_dates.items():
        sell_df = sell_df.append({'Symbol': symbol, 'Date': date, 'Close': close}, ignore_index=True)

# Print buy and sell dataframes
print("Buy Signals:")
print(buy_df)
print("\nSell Signals:")
print(sell_df)
