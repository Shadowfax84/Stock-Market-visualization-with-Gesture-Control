import logging
from django.core.management.base import BaseCommand
import yfinance as yf
import pandas as pd
from ui.models import NiftyData

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch NIFTY 50 Index data and save to the database'

    def handle(self, *args, **kwargs):
        try:
            logger.info('Fetching NIFTY 50 Index data...')
            ticker = "^NSEI"
            start_date = "2018-01-01"
            end_date = "2024-06-14"
            data = yf.download(ticker, start=start_date, end=end_date)

            logger.info('Calculating financial metrics...')
            data['Daily_Return'] = data['Adj Close'].pct_change()
            data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod()
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
            data['Force_Index'] = (data['Close'].diff()
                                   * data['Volume']).cumsum()
            data['Standard_Deviation'] = data['Daily_Return'].rolling(
                window=252).std() * 100
            data['Final_Decision'] = 'Hold'
            data['Market_Condition'] = 'Neutral'

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

            logger.info('Saving data to database...')
            for index, row in data.iterrows():
                stock_data = NiftyData(
                    date=index,
                    adj_close=row['Adj Close'],
                    daily_return=row['Daily_Return'],
                    cumulative_return=row['Cumulative_Return'],
                    sma_50=row['SMA_50'],
                    sma_200=row['SMA_200'],
                    rsi=row['RSI'],
                    upper_bb=row['Upper_BB'],
                    lower_bb=row['Lower_BB'],
                    obv=row['OBV'],
                    force_index=row['Force_Index'],
                    standard_deviation=row['Standard_Deviation'],
                    final_decision=row['Final_Decision'],
                    market_condition=row['Market_Condition']
                )
                stock_data.save()

            logger.info('Successfully fetched and saved NIFTY 50 data.')

        except Exception as e:
            logger.error(f'Error fetching NIFTY 50 data: {e}')
