from django.core.management.base import BaseCommand
import yfinance as yf
from ui.models import Sector, Stock, StockData
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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


class Command(BaseCommand):
    help = 'Fetch NIFTY 50 stock data and save to the database'

    def handle(self, *args, **kwargs):
        try:
            start_date = "2018-01-01"
            end_date = datetime.today().strftime('%Y-%m-%d')

            for stock_name, (ticker, sector_name) in nifty_50_stocks.items():
                logger.info(f'Fetching data for {stock_name} ({ticker})...')

                sector, _ = Sector.objects.get_or_create(name=sector_name)
                stock, _ = Stock.objects.get_or_create(
                    name=stock_name, ticker=ticker, sector=sector)
                data = yf.download(ticker, start=start_date, end=end_date)

                if data.empty:
                    logger.warning(f'No data found for {
                                   stock_name} ({ticker})')
                    continue

                logger.info(f'Calculating financial metrics for {
                            stock_name} ({ticker})...')
                data = self.calculate_metrics(data)

                logger.info(f'Saving data to database for {
                            stock_name} ({ticker})...')
                self.save_data_to_db(data, stock)

            logger.info('Successfully fetched and saved NIFTY 50 stock data.')
            print('NIFTY 50 stock data fetched and saved successfully.')

        except Exception as e:
            logger.error(f'Error fetching NIFTY 50 stock data: {e}')
            print(f'Error fetching NIFTY 50 stock data: {e}')

    def calculate_metrics(self, data):
        data['Daily_Return'] = data['Adj Close'].pct_change() * 100
        data['Cumulative_Return'] = (1 + data['Daily_Return']/100).cumprod()
        data['Open'] = data['Open']
        data['High'] = data['High']
        data['Low'] = data['Low']
        data['Close'] = data['Adj Close']
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        data['Delta'] = data['Close'].diff()
        data['Up'] = data['Delta'].clip(lower=0)
        data['Down'] = data['Delta'].clip(upper=0).abs()
        data['RSI'] = 100 - (100 / (1 + data['Up'].rolling(window=14).mean() /
                             data['Down'].rolling(window=14).mean()))
        data['Rolling_Mean'] = data['Close'].rolling(window=20).mean()
        data['Rolling_STD'] = data['Close'].rolling(window=20).std()
        data['Upper_BB'] = data['Rolling_Mean'] + (data['Rolling_STD'] * 2)
        data['Lower_BB'] = data['Rolling_Mean'] - (data['Rolling_STD'] * 2)
        data['OBV'] = (data['Volume'] * (data['Close'].diff() > 0) -
                       data['Volume'] * (data['Close'].diff() < 0)).cumsum()
        data['Force_Index'] = (data['Close'].diff() * data['Volume']).cumsum()
        data['Standard_Deviation'] = data['Daily_Return'].rolling(
            window=252).std() * 100
        data['Final_Decision'] = 'Hold'
        data['Market_Condition'] = 'Neutral'

        for i in range(1, len(data)):
            ma_dec = self.moving_average_decision(data.iloc[i])
            rsi_dec = self.rsi_decision(data.iloc[i])
            bb_dec = self.bollinger_bands_decision(data.iloc[i])
            obv_dec = self.obv_decision(data.iloc[i], data['OBV'].iloc[i-1])
            force_dec = self.force_index_decision(data.iloc[i])

            decisions = [rsi_dec, bb_dec]
            final_dec = 'Sell' if decisions.count('Sell') > decisions.count('Buy') else (
                'Buy' if decisions.count('Buy') > decisions.count('Sell') else 'Hold')

            market_conditions = [ma_dec, obv_dec, force_dec]
            market_cond = 'Bullish' if market_conditions.count(
                'Bullish') > market_conditions.count('Bearish') else 'Bearish'

            data.at[data.index[i], 'Final_Decision'] = final_dec
            data.at[data.index[i], 'Market_Condition'] = market_cond

        return data

    def moving_average_decision(self, row):
        return 'Bullish' if row['SMA_50'] > row['SMA_200'] else 'Bearish'

    def rsi_decision(self, row):
        if row['RSI'] > 70:
            return 'Sell'
        elif row['RSI'] < 30:
            return 'Buy'
        else:
            return 'Hold'

    def bollinger_bands_decision(self, row):
        if row['Close'] > row['Upper_BB']:
            return 'Sell'
        elif row['Close'] < row['Lower_BB']:
            return 'Buy'
        else:
            return 'Hold'

    def obv_decision(self, row, prev_obv):
        return 'Bullish' if row['OBV'] > prev_obv else 'Bearish'

    def force_index_decision(self, row):
        return 'Bullish' if row['Force_Index'] > 0 else 'Bearish'

    def save_data_to_db(self, data, stock):
        saved_count = 0
        updated_count = 0
        skipped_entries = []

        for index, row in data.iterrows():
            try:
                stock_data, created = StockData.objects.update_or_create(
                    stock=stock,
                    date=index,
                    defaults={
                        'open': row['Open'],
                        'high': row['High'],
                        'low': row['Low'],
                        'close': row['Close'],
                        'daily_return': row['Daily_Return'],
                        'cumulative_return': row['Cumulative_Return'],
                        'sma_50': row['SMA_50'],
                        'sma_200': row['SMA_200'],
                        'rsi': row['RSI'],
                        'upper_bb': row['Upper_BB'],
                        'lower_bb': row['Lower_BB'],
                        'obv': row['OBV'],
                        'force_index': row['Force_Index'],
                        'standard_deviation': row['Standard_Deviation'],
                        'final_decision': row['Final_Decision'],
                        'market_condition': row['Market_Condition']
                    }
                )
                if created:
                    saved_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                skipped_entries.append((index, str(e)))
                logger.error(f'Error saving data for {index}: {str(e)}')

        if saved_count > 0:
            logger.info(f'{saved_count} entries saved successfully.')
        if updated_count > 0:
            logger.info(f'{updated_count} entries updated successfully.')
        if skipped_entries:
            logger.warning(
                f'{len(skipped_entries)} entries were not saved due to errors:')
            for entry in skipped_entries:
                logger.warning(
                    f'Entry for {entry[0]} skipped. Error: {entry[1]}')
