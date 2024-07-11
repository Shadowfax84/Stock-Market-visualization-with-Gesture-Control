import yfinance as yf
import pandas as pd
import os

# Define the NIFTY 50 stocks with their corresponding sectors
nifty_50_stocks = {
    'Adani Enterprises Ltd.': ['ADANIENT.NS', 'Metals & Mining'],
    'Adani Ports and Special Economic Zone Ltd.': ['ADANIPORTS.NS', 'Services'],
    'Apollo Hospitals Enterprise Ltd.': ['APOLLOHOSP.NS', 'Healthcare'],
    'Asian Paints Ltd.': ['ASIANPAINT.NS', 'Consumer Durables'],
    'Axis Bank Ltd.': ['AXISBANK.NS', 'Financial Services'],
    'Bajaj Auto Ltd.': ['BAJAJ-AUTO.NS', 'Automobile and Auto Components'],
    'Bajaj Finance Ltd.': ['BAJFINANCE.NS', 'Financial Services'],
    'Bajaj Finserv Ltd.': ['BAJAJFINSV.NS', 'Financial Services'],
    'Bharat Petroleum Corporation Ltd.': ['BPCL.NS', 'Oil Gas & Consumable Fuels'],
    'Bharti Airtel Ltd.': ['BHARTIARTL.NS', 'Telecommunication'],
    'Britannia Industries Ltd.': ['BRITANNIA.NS', 'Fast Moving Consumer Goods'],
    'Cipla Ltd.': ['CIPLA.NS', 'Healthcare'],
    'Coal India Ltd.': ['COALINDIA.NS', 'Oil Gas & Consumable Fuels'],
    'Divi\'s Laboratories Ltd.': ['DIVISLAB.NS', 'Healthcare'],
    'Dr. Reddy\'s Laboratories Ltd.': ['DRREDDY.NS', 'Healthcare'],
    'Eicher Motors Ltd.': ['EICHERMOT.NS', 'Automobile and Auto Components'],
    'Grasim Industries Ltd.': ['GRASIM.NS', 'Construction Materials'],
    'HCL Technologies Ltd.': ['HCLTECH.NS', 'Information Technology'],
    'HDFC Bank Ltd.': ['HDFCBANK.NS', 'Financial Services'],
    'HDFC Life Insurance Company Ltd.': ['HDFCLIFE.NS', 'Financial Services'],
    'Hero MotoCorp Ltd.': ['HEROMOTOCO.NS', 'Automobile and Auto Components'],
    'Hindalco Industries Ltd.': ['HINDALCO.NS', 'Metals & Mining'],
    'Hindustan Unilever Ltd.': ['HINDUNILVR.NS', 'Fast Moving Consumer Goods'],
    'ICICI Bank Ltd.': ['ICICIBANK.NS', 'Financial Services'],
    'ITC Ltd.': ['ITC.NS', 'Fast Moving Consumer Goods'],
    'IndusInd Bank Ltd.': ['INDUSINDBK.NS', 'Financial Services'],
    'Infosys Ltd.': ['INFY.NS', 'Information Technology'],
    'JSW Steel Ltd.': ['JSWSTEEL.NS', 'Metals & Mining'],
    'Kotak Mahindra Bank Ltd.': ['KOTAKBANK.NS', 'Financial Services'],
    'LTIMindtree Ltd.': ['LTIM.NS', 'Information Technology'],
    'Larsen & Toubro Ltd.': ['LT.NS', 'Construction'],
    'Mahindra & Mahindra Ltd.': ['M&M.NS', 'Automobile and Auto Components'],
    'Maruti Suzuki India Ltd.': ['MARUTI.NS', 'Automobile and Auto Components'],
    'NTPC Ltd.': ['NTPC.NS', 'Power'],
    'Nestle India Ltd.': ['NESTLEIND.NS', 'Fast Moving Consumer Goods'],
    'Oil & Natural Gas Corporation Ltd.': ['ONGC.NS', 'Oil Gas & Consumable Fuels'],
    'Power Grid Corporation of India Ltd.': ['POWERGRID.NS', 'Power'],
    'Reliance Industries Ltd.': ['RELIANCE.NS', 'Oil Gas & Consumable Fuels'],
    'SBI Life Insurance Company Ltd.': ['SBILIFE.NS', 'Financial Services'],
    'Shriram Finance Ltd.': ['SHRIRAMFIN.NS', 'Financial Services'],
    'State Bank of India': ['SBIN.NS', 'Financial Services'],
    'Sun Pharmaceutical Industries Ltd.': ['SUNPHARMA.NS', 'Healthcare'],
    'Tata Consultancy Services Ltd.': ['TCS.NS', 'Information Technology'],
    'Tata Consumer Products Ltd.': ['TATACONSUM.NS', 'Fast Moving Consumer Goods'],
    'Tata Motors Ltd.': ['TATAMOTORS.NS', 'Automobile and Auto Components'],
    'Tata Steel Ltd.': ['TATASTEEL.NS', 'Metals & Mining'],
    'Tech Mahindra Ltd.': ['TECHM.NS', 'Information Technology'],
    'Titan Company Ltd.': ['TITAN.NS', 'Consumer Durables'],
    'UltraTech Cement Ltd.': ['ULTRACEMCO.NS', 'Construction Materials'],
    'Wipro Ltd.': ['WIPRO.NS', 'Information Technology']
}

# Define the date range
start_date = "2018-01-01"
end_date = "2024-06-14"

# Function to calculate technical indicators and decisions


def analyze_stock(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        return None

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
            market_condition = 'Bullish'
        elif market_conditions.count('Bearish') > market_conditions.count('Bullish'):
            market_condition = 'Bearish'
        else:
            market_condition = 'Neutral'

        data.at[data.index[i], 'Final_Decision'] = final_dec
        data.at[data.index[i], 'Market_Condition'] = market_condition

    return data


# Base directory for storing the files
base_directory = "nifty_50_data"

# Ensure the base directory exists
os.makedirs(base_directory, exist_ok=True)

# Create directories for each sector
sectors = set(stock[1] for stock in nifty_50_stocks.values())
for sector in sectors:
    os.makedirs(os.path.join(base_directory, sector), exist_ok=True)

# Analyze each stock and save the result in its respective sector directory
for stock_name, (ticker, sector) in nifty_50_stocks.items():
    analyzed_data = analyze_stock(ticker, start_date, end_date)
    if analyzed_data is not None:
        sector_directory = os.path.join(base_directory, sector)
        file_path = os.path.join(sector_directory, f"{
                                 stock_name.replace(' ', '_')}.csv")
        analyzed_data.to_csv(file_path)
        print(f"Saved data for {stock_name} to {file_path}")
    else:
        print(f"Failed to retrieve data for {stock_name}")
