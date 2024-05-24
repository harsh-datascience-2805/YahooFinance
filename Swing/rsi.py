import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.utils import dropna

def get_signals(df):
    # Create a 'Signal' column and initialize with 'Hold'
    df['Signal'] = 'Hold'

    # Generate 'Buy' signals
    df.loc[df['RSI'] < 30, 'Signal'] = 'Buy'

    # Generate 'Sell' signals
    df.loc[df['RSI'] > 70, 'Signal'] = 'Sell'

    return df

# Define the symbols
symbols = ['ABB.NS', 'ADANIENSOL.NS', 'ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS', 'ATGL.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS', 'ASIANPAINT.NS', 'DMART.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BAJAJHLDNG.NS', 'BANKBARODA.NS', 'BERGEPAINT.NS', 'BEL.NS', 'BPCL.NS', 'BHARTIARTL.NS', 'BOSCHLTD.NS', 'BRITANNIA.NS', 'CANBK.NS', 'CHOLAFIN.NS', 'CIPLA.NS', 'COALINDIA.NS', 'COLPAL.NS', 'DLF.NS', 'DABUR.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GAIL.NS', 'GODREJCP.NS', 'GRASIM.NS', 'HCLTECH.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HAVELLS.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HAL.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'ITC.NS', 'IOC.NS', 'IRCTC.NS', 'IRFC.NS', 'INDUSINDBK.NS', 'NAUKRI.NS', 'INFY.NS', 'INDIGO.NS', 'JSWSTEEL.NS', 'JINDALSTEL.NS', 'JIOFIN.NS', 'KOTAKBANK.NS', 'LTIM.NS', 'LT.NS', 'LICI.NS', 'M&M.NS', 'MARICO.NS', 'MARUTI.NS', 'NTPC.NS', 'NESTLEIND.NS', 'ONGC.NS', 'PIDILITIND.NS', 'PFC.NS', 'POWERGRID.NS', 'PNB.NS', 'RECLTD.NS', 'RELIANCE.NS', 'SBICARD.NS', 'SBILIFE.NS', 'SRF.NS', 'MOTHERSON.NS', 'SHREECEM.NS', 'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SBIN.NS', 'SUNPHARMA.NS', 'TVSMOTOR.NS', 'TCS.NS', 'TATACONSUM.NS', 'TATAMTRDVR.NS', 'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS', 'TORNTPHARM.NS', 'TRENT.NS', 'ULTRACEMCO.NS', 'MCDOWELL-N.NS', 'VBL.NS', 'VEDL.NS', 'WIPRO.NS', 'ZOMATO.NS', 'ZYDUSLIFE.NS']

# Create an empty DataFrame to store the RSI values and signals
signals_df = pd.DataFrame()

for symbol in symbols:
    # Download stock data from Yahoo Finance
    stock = yf.Ticker(symbol)
    df = stock.history(period="max")

    # Ensure the dataframe does not contain NaN values
    df = dropna(df)

    # Calculate RSI
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()

    # Add the symbol column
    df['Symbol'] = symbol

    # Generate signals based on RSI
    df = get_signals(df)

    # Get the most recent row if df is not empty
    if not df.empty:
        df = df.iloc[[-1]]

        # Append the data to the signals_df DataFrame
        signals_df = pd.concat([signals_df, df[['Symbol', 'Close', 'RSI', 'Signal']]])

# Export the DataFrame to a CSV file
signals_df.to_csv('rsi_signals.csv', index_label='Date')
