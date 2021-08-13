from google.cloud import datastore
import yfinance as yahooFinance
import datetime
import pytz

market_day_kind = 'MarketDay'

def get_most_recent_market_day(datastore_client):
    query = datastore_client.query(kind=market_day_kind)
    query.order = ['-Date']
    most_recent = query.fetch(limit=1)

    return most_recent

def run_daily_market_summary_update(datastore_client):
    # Find the latest date in the datastore
    most_recent = get_most_recent_market_day(datastore_client)

    # If its not up-to-date, then build all the missing dates up to yesterday.
    most_recent = list(most_recent)

    if most_recent:
        print('most_recent', most_recent[0])
        most_recent = most_recent[0]['Date'].date()
        start_date = most_recent + datetime.timedelta(days = 1)
    else:
        print('no market days in datastore')
        start_date = datetime.datetime(2014, 9, 17).date()

    timezone = pytz.timezone('America/New_York')
    today = datetime.datetime.now(timezone).date()
    yesterday = today - datetime.timedelta(days = 1)

    print('start date:', start_date)
    # print('today:', today)
    print('yesterday:', yesterday)

    if start_date < today:
        btc = yahooFinance.Ticker("BTC-USD")
        history = btc.history(start=start_date, end=yesterday)
        history['Date'] = history.index
        history_series = history.T.to_dict('series')

        entities = [datastore.Entity(key=datastore_client.key(market_day_kind)) for i in range(len(history))]

        for entity, update_dict in zip(entities, history_series.items()):
            # print('update_dict', update_dict[1])
            entity.update(update_dict[1])

        # Save to google datastore. Max supported is 500 per call.
        batchsize = 500

        for i in range(0, len(entities), batchsize):
            batch = entities[i:i+batchsize]
            datastore_client.put_multi(batch)

        return "Updated datastore market days starting from " + start_date.strftime('%m/%d/%Y')

    else:
        return "Datastore is update-to-date!"

def get_market_days_starting_from(datastore_client, start_date):
    query = datastore_client.query(kind=market_day_kind)
    query.order = ['-Date']
    query.add_filter('Date', '>=', start_date)
    results = query.fetch()

    return results
