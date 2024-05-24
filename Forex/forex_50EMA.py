import pandas as pd
import ta
import yfinance as yf

def fetch_data(ticker, period="1y"):
    """ Fetch historical forex data from Yahoo Finance """
    df = yf.download(ticker, period=period)
    if df.empty:
        print(f"No data fetched for {ticker}.")
    return df

def calculate_ema(df, period=50):
    """ Calculate the Exponential Moving Average (EMA) """
    if 'Close' not in df:
        return df
    df['EMA'] = ta.trend.ema_indicator(df['Close'], window=period)
    return df

def identify_structure(df):
    """ Identify structure levels """
    df['Swing_High'] = df['High'][(df['High'] > df['High'].shift(1)) & (df['High'] > df['High'].shift(-1))]
    df['Swing_Low'] = df['Low'][(df['Low'] < df['Low'].shift(1)) & (df['Low'] < df['Low'].shift(-1))]
    
    df['Structure_High'] = df['Swing_High'].rolling(window=30).apply(lambda x: x.count() >= 2, raw=False)
    df['Structure_Low'] = df['Swing_Low'].rolling(window=30).apply(lambda x: x.count() >= 2, raw=False)
    
    df['Structure_High'] = df['Structure_High'].ffill().bfill()
    df['Structure_Low'] = df['Structure_Low'].ffill().bfill()
    
    return df

def generate_signals(df, pair):
    """ Generate buy and sell signals based on refined strategy rules """
    buy_signals = []
    sell_signals = []
    
    if 'EMA' not in df:
        return buy_signals, sell_signals

    for i in range(1, len(df)):
        # Bullish entry rules
        if (
            df['Close'].iloc[i] > df['EMA'].iloc[i] and 
            df['High'].iloc[i] > df['High'].rolling(window=50).max().shift(1).iloc[i] and
            df['Low'].iloc[i] <= df['EMA'].iloc[i] and
            df['Structure_High'].iloc[i]
        ):
            if df['Close'].iloc[i] > df['Open'].iloc[i]:  # Buying pressure
                stop_loss = df['Low'].rolling(window=5).min().iloc[i]
                target = df['Close'].iloc[i] + 2 * (df['Close'].iloc[i] - stop_loss)
                buy_signals.append((df.index[i], pair, df['Close'].iloc[i], stop_loss, target))
        
        # Bearish entry rules
        if (
            df['Close'].iloc[i] < df['EMA'].iloc[i] and 
            df['Low'].iloc[i] < df['Low'].rolling(window=50).min().shift(1).iloc[i] and
            df['High'].iloc[i] >= df['EMA'].iloc[i] and
            df['Structure_Low'].iloc[i]
        ):
            if df['Close'].iloc[i] < df['Open'].iloc[i]:  # Selling pressure
                stop_loss = df['High'].rolling(window=5).max().iloc[i]
                target = df['Close'].iloc[i] - 2 * (stop_loss - df['Close'].iloc[i])
                sell_signals.append((df.index[i], pair, df['Close'].iloc[i], stop_loss, target))
    
    return buy_signals, sell_signals

def process_pair(pair):
    # Fetch data
    df = fetch_data(pair)
    
    if df.empty:
        return [], []
    
    # Calculate 50 EMA
    df = calculate_ema(df)
    
    # Identify structure levels
    df = identify_structure(df)
    
    # Generate buy and sell signals
    buy_signals, sell_signals = generate_signals(df, pair)
    
    return buy_signals, sell_signals

def main(pairs):
    all_buy_signals = []
    all_sell_signals = []
    no_signals = True  # Flag to check if any signals are generated for any pair
    for pair in pairs:
        buy_signals, sell_signals = process_pair(pair)
        if buy_signals or sell_signals:
            no_signals = False
        all_buy_signals.extend(buy_signals)
        all_sell_signals.extend(sell_signals)
    
    if no_signals:
        print("No signals at the moment.")
        return
    
    # Combine buy and sell signals into one DataFrame
    buy_df = pd.DataFrame(all_buy_signals, columns=['Date', 'Pair', 'Entry', 'Stop Loss', 'Target'])
    sell_df = pd.DataFrame(all_sell_signals, columns=['Date', 'Pair', 'Entry', 'Stop Loss', 'Target'])
    signals_df = pd.concat([buy_df, sell_df])
    signals_df.sort_values(by='Date', inplace=True)
    
    return signals_df

# Example list of forex pairs (you need to provide the actual list)
# forex_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X']

forex_pairs = ['CADUSD=X', 'CADEUR=X', 'CADGBP=X', 'CADCNY=X', 'EURUSD=X', 'JPY=X', 'GBPUSD=X', 'CHF=X', 'AUDUSD=X', 'AUDJPY=X', 'NZDUSD=X', 'EURJPY=X', 'GBPJPY=X', 'EURGBP=X', 'EURSEK=X', 'EURCHF=X', 'EURHUF=X', 'EURJPY=X', 'CNY=X', 'USDHKD=X', 'USDSGD=X', 'USDINR=X', 'USDMXN=X', 'USDPHP=X', 'USDIDR=X', 'USDTHB=X', 'USDMYR=X', 'USDZAR=X', 'USDRUB=X']

signals_df = main(forex_pairs)

# Save signals to a single CSV file
if not signals_df.empty:
    signals_df.to_csv("forex_signals.csv", index=False)
    print("All signals saved to forex_signals.csv")
else:
    print("No signals generated.")
