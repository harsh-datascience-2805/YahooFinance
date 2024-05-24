import yfinance as yf
import pandas as pd
import ta
import requests

# Download stock data from Yahoo Finance
ticker = "AAPL"
stock = yf.Ticker(ticker)
df = stock.history(period="max")

# Calculate technical indicators
df['SMA50'] = ta.sma(df['Close'], length=50)
df['SMA200'] = ta.sma(df['Close'], length=200)
df['RSI'] = ta.rsi(df['Close'], length=14)  # RSI indicator

# Check if price crosses above/below moving averages
df['CrossedAbove50'] = df['Close'].gt(df['SMA50']).diff().gt(0)
df['CrossedBelow50'] = df['Close'].lt(df['SMA50']).diff().lt(0)
df['CrossedAbove200'] = df['Close'].gt(df['SMA200']).diff().gt(0)
df['CrossedBelow200'] = df['Close'].lt(df['SMA200']).diff().lt(0)

# Identify support and resistance levels
df['Support'] = ta.pivot_points(df['High'], df['Low'], df['Close'], mode='sup')
df['Resistance'] = ta.pivot_points(df['High'], df['Low'], df['Close'], mode='res')

# Check if price is near support or resistance
df['NearSupport'] = df['Close'].between(df['Support'] * 0.99, df['Support'] * 1.01)
df['NearResistance'] = df['Close'].between(df['Resistance'] * 0.99, df['Resistance'] * 1.01)

# Identify chart patterns (e.g., double top/bottom)
df['DoubleTop'] = ta.cdl_pattern(df['Open'], df['High'], df['Low'], df['Close'], name='CDLDOUBLETO')
df['DoubleBottom'] = ta.cdl_pattern(df['Open'], df['High'], df['Low'], df['Close'], name='CDLDOBBLEBO')

# Option chain analysis
def get_option_chain(ticker):
    url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
    response = requests.get(url)
    data = response.json()
    calls = data['optionChain']['result'][0]['quotes']
    puts = data['optionChain']['result'][0]['puts']
    return calls, puts

calls, puts = get_option_chain(ticker)

# Calculate option chain metrics (e.g., put/call ratio)
total_call_vol = sum(call['volume'] for call in calls)
total_put_vol = sum(put['volume'] for put in puts)
put_call_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else 0

# Filter for stocks meeting swing trading criteria
buy_signals = (
    df['CrossedAbove50'] & df['CrossedAbove200'] &
    df['NearSupport'] & (df['DoubleBottom'] > 0) &
    (df['RSI'].shift(1) < 30) & (put_call_ratio < 0.7)
)
sell_signals = (
    df['CrossedBelow50'] & df['CrossedBelow200'] &
    df['NearResistance'] & (df['DoubleTop'] > 0) &
    (df['RSI'].shift(1) > 70) & (put_call_ratio > 1.3)
)

# Print dates with buy/sell signals
print('Buy Signals:')
print(df.loc[buy_signals.shift(1), 'Close'])
print('\nSell Signals:')
print(df.loc[sell_signals.shift(1), 'Close'])
