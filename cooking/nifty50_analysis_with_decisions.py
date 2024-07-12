import yfinance as yf
import pandas as pd

# Retrieve NIFTY 50 Index Data
ticker = "^NSEI"
start_date = "2018-01-01"
end_date = "2024-06-14"
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate daily returns
data['Daily_Return'] = data['Adj Close'].pct_change() * 100

# Calculate cumulative returns
data['Cumulative_Return'] = (1 + data['Daily_Return']/100).cumprod()

# Calculate open, high, low, and close
data['Open'] = data['Open']
data['High'] = data['High']
data['Low'] = data['Low']
data['Close'] = data['Adj Close']

# Calculate Simple Moving Averages (SMA)
data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()

# Calculate Relative Strength Index (RSI)
data['Delta'] = data['Close'].diff()
data['Up'] = data['Delta'].clip(lower=0)
data['Down'] = data['Delta'].clip(upper=0).abs()
data['RSI'] = 100 - (100 / (1 + data['Up'].rolling(window=14).mean() /
                     data['Down'].rolling(window=14).mean()))

# Calculate Bollinger Bands
data['Rolling_Mean'] = data['Close'].rolling(window=20).mean()
data['Rolling_STD'] = data['Close'].rolling(window=20).std()
data['Upper_BB'] = data['Rolling_Mean'] + (data['Rolling_STD'] * 2)
data['Lower_BB'] = data['Rolling_Mean'] - (data['Rolling_STD'] * 2)

# Calculate On Balance Volume (OBV)
data['OBV'] = (data['Volume'] * (data['Close'].diff() > 0) -
               data['Volume'] * (data['Close'].diff() < 0)).cumsum()

# Calculate Force Index
data['Force_Index'] = (data['Close'].diff() * data['Volume']).cumsum()

# Calculate Standard Deviation
data['Standard_Deviation'] = data['Daily_Return'].rolling(
    window=252).std() * 100

# Initialize columns for decisions
data['Final_Decision'] = 'Hold'
data['Market_Condition'] = 'Neutral'

# Decision functions


def moving_average_decision(row):
    if row['SMA_50'] > row['SMA_200']:
        return 'Bullish'
    else:
        return 'Bearish'


def rsi_decision(row):
    if row['RSI'] > 70:
        return 'Sell'
    elif row['RSI'] < 30:
        return 'Buy'
    else:
        return 'Hold'


def bollinger_bands_decision(row):
    if row['Close'] > row['Upper_BB']:
        return 'Sell'
    elif row['Close'] < row['Lower_BB']:
        return 'Buy'
    else:
        return 'Hold'


def obv_decision(row, prev_obv):
    if row['OBV'] > prev_obv:
        return 'Bullish'
    else:
        return 'Bearish'


def force_index_decision(row):
    if row['Force_Index'] > 0:
        return 'Bullish'
    else:
        return 'Bearish'


# Iterate through the data to calculate decisions for each day
for i in range(1, len(data)):
    ma_dec = moving_average_decision(data.iloc[i])
    rsi_dec = rsi_decision(data.iloc[i])
    bb_dec = bollinger_bands_decision(data.iloc[i])
    obv_dec = obv_decision(data.iloc[i], data['OBV'].iloc[i-1])
    force_dec = force_index_decision(data.iloc[i])

    decisions = [rsi_dec, bb_dec]
    if decisions.count('Sell') > decisions.count('Buy'):
        final_dec = 'Sell'
    elif decisions.count('Buy') > decisions.count('Sell'):
        final_dec = 'Buy'
    else:
        final_dec = 'Hold'

    market_conditions = [ma_dec, obv_dec, force_dec]
    if market_conditions.count('Bullish') > market_conditions.count('Bearish'):
        market_cond = 'Bullish'
    else:
        market_cond = 'Bearish'

    data.at[data.index[i], 'Final_Decision'] = final_dec
    data.at[data.index[i], 'Market_Condition'] = market_cond

# Display the last few rows of the data
print(data.tail())
print(data.columns)

# Export processed data to CSV
# data.to_csv('nifty50_analysis_with_decisions.csv')
