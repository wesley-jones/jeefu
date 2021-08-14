import yfinance as yahooFinance
import datetime
from utilities import constants, utility

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

        # Save data to google datastore
        utility.save_to_datastore(datastore_client, kind, dictionaries)

        for x in dictionaries:
            print('Added MarketDay for', x[constants.DATE].date())

        return "Updated datastore market days starting from " + start_date.strftime('%m/%d/%Y')

    else:
        return "Datastore is update-to-date!"
