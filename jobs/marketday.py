import yfinance as yahooFinance
import datetime
from utilities import constants, utility
import pandas as pd
import numpy as np

kind = 'MarketDay'

def run_daily_market_summary_update(datastore_client):
    # Find the latest date in the datastore
    most_recent = utility.get_most_recent_entity(datastore_client, kind)

    # If its not up-to-date, then build all the missing dates up to yesterday.
    most_recent = list(most_recent)

    if most_recent:
        most_recent = most_recent[0][constants.DATE].date()
        print('most_recent', most_recent)
        start_date = most_recent + datetime.timedelta(days = 1)
    else:
        print('no market days in datastore')
        start_date = constants.HISTORICAL_START_DATE

    yesterday = utility.get_yesterday()

    if start_date < utility.get_today():
        # Get BTC Historical Data from Yahoo
        btc = yahooFinance.Ticker("BTC-USD")
        history = btc.history(start=start_date, end=yesterday)
        history[constants.DATE] = history.index
        history_series = history.T.to_dict('series')
        list_of_tuples = history_series.items()
        dictionaries = [i[1] for i in list_of_tuples]

        missing_data = add_missing_yahoo_data(start_date)
        dictionaries += missing_data

        # Save data to google datastore
        utility.save_to_datastore(datastore_client, kind, dictionaries)

        for x in dictionaries:
            print('Added MarketDay for', x[constants.DATE].date())

        return "Updated datastore market days starting from " + start_date.strftime('%m/%d/%Y')

    else:
        return "Market Day Summaries are update-to-date!"

def add_missing_yahoo_data(start_date):
    dictionaries = []

    # Data is missing for April 17th, 2020 from Yahoo
    if start_date <= datetime.datetime(2020, 4, 17).date():
        dictionary = {
            constants.CLOSE_PRICE: 7083.3,
            constants.DATE: datetime.datetime(2020, 4, 17),
            constants.OPEN_PRICE: 7084.6,
            constants.LOW_PRICE: 7031.5,
            constants.HIGH_PRICE: 7105.9
        }
        dictionaries.append(dictionary)

    # Data is missing for Oct 9th, 2020 from Yahoo
    if start_date <= datetime.datetime(2020, 10, 9).date():
        dictionary = {
            constants.CLOSE_PRICE: 11419.8,
            constants.DATE: datetime.datetime(2020, 10, 9),
            constants.OPEN_PRICE: 10889.9,
            constants.LOW_PRICE: 11053.5,
            constants.HIGH_PRICE: 11475
        }
        dictionaries.append(dictionary)

    # Data is missing for Oct 12th, 2020 from Yahoo
    if start_date <= datetime.datetime(2020, 10, 12).date():
        dictionary = {
            constants.CLOSE_PRICE: 11469.1,
            constants.DATE: datetime.datetime(2020, 10, 12),
            constants.OPEN_PRICE: 11386.4,
            constants.LOW_PRICE: 11436.9,
            constants.HIGH_PRICE: 11540.4
        }
        dictionaries.append(dictionary)

    # Data is missing for Oct 13th, 2020 from Yahoo
    if start_date <= datetime.datetime(2020, 10, 13).date():
        dictionary = {
            constants.CLOSE_PRICE: 11442.7,
            constants.DATE: datetime.datetime(2020, 10, 13),
            constants.OPEN_PRICE: 11457.4,
            constants.LOW_PRICE: 11413.8,
            constants.HIGH_PRICE: 11485.6
        }
        dictionaries.append(dictionary)

    return dictionaries

def get_yahoo_data():
    # Get BTC Historical Data from Yahoo
    btc = yahooFinance.Ticker("BTC-USD")
    history = btc.history(start=constants.HISTORICAL_START_DATE, end=utility.get_yesterday())
    history.to_csv('btc_history.csv')

def get_market_day_metrics(datastore_client):
    entities = utility.get_all_entities_by_kind(datastore_client, kind)
    df = pd.DataFrame(entities)

    df['percent_change'] = df[constants.CLOSE_PRICE].pct_change()
    df['diff'] = df[constants.CLOSE_PRICE].diff()
    df['percent_change_abs'] = df[constants.CLOSE_PRICE].pct_change().abs()
    df['diff_abs'] = df[constants.CLOSE_PRICE].diff().abs()
    # print(df.head())

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_names = df[constants.DATE].dt.day_name()
    print('Avg Percent Change:', df['percent_change'].groupby(day_names).mean().reindex(days))
    # print('Avg Absolute Percent Change:', df['percent_change_abs'].groupby(day_names).mean().reindex(days))
    # print('Avg Daily Price Change:', df['diff'].groupby(day_names).mean().reindex(days))
    # print('Avg Absolute Daily Price Change:', df['diff_abs'].groupby(day_names).mean().reindex(days))

    # Sums
    # print('Sum Daily Price Change:', df['diff'].groupby(day_names).sum().reindex(days))
    # print('Sum Absolute Daily Price Change:', df['diff_abs'].groupby(day_names).sum().reindex(days))

    # print('Total Average Percentage change:',df['percent_change'].mean())
    # print(df[['Close', 'diff', 'percent_change']])
    

if __name__ == "__main__":
    from google.cloud import datastore
    datastore_client = datastore.Client()
    get_market_day_metrics(datastore_client)
