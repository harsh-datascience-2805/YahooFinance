import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator

# Function to fetch historical stock data from Yahoo Finance
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    return df

# Define stock ticker and date range
ticker = "ORC.DE"
start_date = "2010-01-01"
end_date = "2024-05-23"

# Fetch historical stock data
df = fetch_stock_data(ticker, start_date, end_date)

# Calculate technical indicators
df['SMA50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
df['SMA200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()

# Define features (technical indicators) and target (price movement)
features = ['SMA50', 'SMA200', 'RSI']
target = 'PriceMovement'  # 1 for price increase, 0 for price decrease or no change

# Create target variable based on price movement
df['PriceMovement'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)

# Drop NaN values and unnecessary columns
df.dropna(inplace=True)
df = df[features + [target]]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)

# Train Random Forest classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predict on test set
y_pred = clf.predict(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

# Example usage: Predict price movement for a new data point
new_data_point = pd.DataFrame([[50, 200, 70]], columns=features)
predicted_price_movement = clf.predict(new_data_point)
print(f"Predicted price movement: {'Increase' if predicted_price_movement == 1 else 'Decrease or No Change'}")
