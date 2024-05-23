import pandas as pd
import ta
import yfinance as yf

def fetch_data(ticker, period="1y"):
    """ Fetch historical forex data from Yahoo Finance """
    df = yf.download(ticker, period=period)
    return df

def calculate_ema(df, period=50):
    """ Calculate the Exponential Moving Average (EMA) """
    df['EMA'] = ta.trend.ema_indicator(df['Close'], window=period)
    return df

def identify_structure(df, lookback=30):
    """ Identify structure levels tested at least twice """
    df['Swing_High'] = df['High'][(df['High'] > df['High'].shift(1)) & (df['High'] > df['High'].shift(-1))]
    df['Swing_Low'] = df['Low'][(df['Low'] < df['Low'].shift(1)) & (df['Low'] < df['Low'].shift(-1))]
    
    df['Structure_High'] = df['Swing_High'][df['Swing_High'].rolling(window=lookback).count() >= 2]
    df['Structure_Low'] = df['Swing_Low'][df['Swing_Low'].rolling(window=lookback).count() >= 2]
    
    return df

def generate_signals(df):
    """ Generate buy and sell signals based on refined strategy rules """
    buy_signals = []
    sell_signals = []
    
    for i in range(1, len(df)):
        # Bullish entry rules
        if (
            df['Close'].iloc[i] > df['EMA'].iloc[i] and 
            df['High'].iloc[i] > df['High'].rolling(window=50).max().shift(1).iloc[i] and
            df['Low'].iloc[i] <= df['EMA'].iloc[i] and
            pd.notna(df['Structure_High'].iloc[i])
        ):
            if df['Close'].iloc[i] > df['Open'].iloc[i]:  # Buying pressure
                stop_loss = df['Low'].rolling(window=5).min().iloc[i]
                target = df['Close'].iloc[i] + 2 * (df['Close'].iloc[i] - stop_loss)
                buy_signals.append((df.index[i], df['Close'].iloc[i], stop_loss, target))
        
        # Bearish entry rules
        if (
            df['Close'].iloc[i] < df['EMA'].iloc[i] and 
            df['Low'].iloc[i] < df['Low'].rolling(window=50).min().shift(1).iloc[i] and
            df['High'].iloc[i] >= df['EMA'].iloc[i] and
            pd.notna(df['Structure_Low'].iloc[i])
        ):
            if df['Close'].iloc[i] < df['Open'].iloc[i]:  # Selling pressure
                stop_loss = df['High'].rolling(window=5).max().iloc[i]
                target = df['Close'].iloc[i] - 2 * (stop_loss - df['Close'].iloc[i])
                sell_signals.append((df.index[i], df['Close'].iloc[i], stop_loss, target))
    
    return buy_signals, sell_signals

def process_pair(pair):
    # Fetch data
    df = fetch_data(pair)
    
    # Calculate 50 EMA
    df = calculate_ema(df)
    
    # Identify structure levels
    df = identify_structure(df)
    
    # Generate buy and sell signals
    buy_signals, sell_signals = generate_signals(df)
    
    return buy_signals, sell_signals

def main(pairs):
    all_signals = {}
    for pair in pairs:
        print(f"Processing {pair}...")
        buy_signals, sell_signals = process_pair(pair)
        all_signals[pair] = {'buy': buy_signals, 'sell': sell_signals}
        print(f"Signals for {pair} processed.")
    return all_signals

if __name__ == "__main__":
    forex_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X']  # Add more pairs as needed
    signals = main(forex_pairs)
    
    # Save signals to CSV files
    for pair, signal_data in signals.items():
        buy_df = pd.DataFrame(signal_data['buy'], columns=['Date', 'Entry', 'Stop Loss', 'Target'])
        sell_df = pd.DataFrame(signal_data['sell'], columns=['Date', 'Entry', 'Stop Loss', 'Target'])
        
        buy_df.to_csv(f"{pair}_buy_signals.csv", index=False)
        sell_df.to_csv(f"{pair}_sell_signals.csv", index=False)
        
        print(f"Buy signals for {pair} saved to {pair}_buy_signals.csv")
        print(f"Sell signals for {pair} saved to {pair}_sell_signals.csv")
