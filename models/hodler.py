# Hodlers Never Sell!!

from google.cloud import datastore
import datetime
import pytz
from jobs import marketday

kind = 'Hodler'
''' 
Example structure
{
	Date: '2021-10-10 00:00:00', (save)
	Recommendation: 'Hold', (save)
    Action: 'Sell', (save)
	- Total Return: .44, (need final and starting balance)
	Cash Balance: 2,222.44, (save)
	BTC Balance: 0, (save)
	Avg Days Holding Cash: 23, (save)
	Avg Days Holding BTC: 72, (save)
	Avg Return per Buy:  .43, (save)
	Avg Return per Sell: .44 (save)
}
'''


def run_daily_hodler_update(datastore_client):
    # Find the latest date in the datastore
    most_recent = get_most_recent_hodler_day(datastore_client)

    # If its not up-to-date, then build all the missing dates up to yesterday.
    most_recent = list(most_recent)

    if most_recent:
        print('most_recent', most_recent[0])
        most_recent = most_recent[0]['Date'].date()
        start_date = most_recent + datetime.timedelta(days = 1)
    else:
        print('no hodler days in datastore')
        start_date = datetime.datetime(2014, 9, 17).date()


    ### Retrieve required data for model
    # Query for market days that haven't been modeled
    # Validate market days
    # Loop thru market days and run model to get recommendation
    # 	calculate metrics
    # 	store entity
    # after loop save all entities to datastore
    market_days = marketday.get_market_days_starting_from(datastore_client, start_date)
    market_days_list = list(market_days)
    print('market_days:', list(market_days_list))

    if market_days_list:
        for market_day in market_days_list:
    else:
        return "No new data to process"

    # print([x for x in market_days])





  # timezone = pytz.timezone('America/New_York')
  # today = datetime.datetime.now(timezone).date()
  # one_day = datetime.timedelta(days = 1)
  # # yesterday = today - datetime.timedelta(days = 1)

  # loop_date = start_date

  # while loop_date < today:

  # 	# Do stuff
  # 	print(loop_date)
  # 	loop_date += one_day

    return "Success"


def get_most_recent_hodler_day(datastore_client):
    query = datastore_client.query(kind=hodler_kind)
    query.order = ['-Date']
    most_recent = query.fetch(limit=1)

    return most_recent

