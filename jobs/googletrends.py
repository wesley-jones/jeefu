## INITIAL COMMENTS ##
# Re-scale Trends data so that all values are on the same scale.
# Reference: https://github.com/e-271/pytrends/blob/master/pytrends/renormalize.py

## SETUP ##
from datetime import datetime, timedelta, date
from numpy import average
from pytrends.request import TrendReq
import time
import pandas as pd
from utilities import utility, constants

filename = 'google_trends.pickle'
overlap=40
kind = 'GoogleTrend'


def run_daily_google_trends_update(datastore_client):
    dictionaries = []

    # Find the latest date in the datastore
    most_recent = utility.get_most_recent_entity(datastore_client, kind)
    most_recent = list(most_recent)

    # If its empty, then build all the missing dates up to this week.
    if most_recent:
        most_recent = most_recent[0]
        print('most_recent_date', most_recent[constants.DATE].date())
        if most_recent[constants.DATE].date() >= utility.get_yesterday():
            return "Google Trends are update-to-date!"

        elif most_recent[constants.DATE].date() < utility.get_today() - timedelta(days = 7):
            return 'Google Trends data in datastore is too far out of sync. You may need to delete all GoogleTrend entities and run this job again.'
    else:
        print('No Google trends in datastore. Proceeding to populate entities.')
        # Start from the beginning
        df = get_interest_over_time(constants.HISTORICAL_START_DATE)
        
        # Convert data to list of dictionaries
        df['Date'] = df.index
        df = df.rename(columns={'Bitcoin': 'Trend'})
        df = df.drop('isPartial', axis=1)
        dictionaries = df.to_dict('records')
        most_recent = dictionaries[-1]

    # Do hourly API calls to generate the data for the days for this week
    hourly_df = get_hourly_interest_over_time(most_recent)

    # append hourly trend values to dictionaries
    hourly_df = hourly_df['Bitcoin']
    hourly_df['Date'] = pd.to_datetime(hourly_df.index)
    hourly_df = hourly_df.rename(columns={'mean': 'Trend'})
    hourly_dictionaries = hourly_df.to_dict('records')
    dictionaries = dictionaries + hourly_dictionaries

    # Save data to google datastore
    utility.save_to_datastore(datastore_client, kind, dictionaries)

    for x in dictionaries:
        print('Added GoogleTrend for', x[constants.DATE].date())

    return "Updated datastore Google Trends starting from " + (most_recent[constants.DATE].date() + timedelta(days=1)).strftime('%m/%d/%Y')

def save_to_disk(df):
    df.to_pickle(filename)

def load_from_disk():
    return pd.read_pickle(filename)

def get_hourly_interest_over_time(most_recent):
    kw_list = ["Bitcoin"]
    pytrends = TrendReq(hl='en-US', tz=300)
    yesterday = utility.get_yesterday()
    start_date = most_recent['Date'].date()

    df = pytrends.get_historical_interest(
        kw_list, 
        year_start=start_date.year, 
        month_start=start_date.month, 
        day_start=start_date.day, 
        hour_start=0,
        year_end=yesterday.year,
        month_end=yesterday.month,
        day_end=yesterday.day,
        hour_end=23,
        cat=0, 
        geo='',
        gprop='',
        sleep=10
    )

    # Scale the trend values based on the most recent
    # entity from the datastore.
    overlap_date = utility.cast_date_to_datetime(start_date)
    overlap_end_date = overlap_date + timedelta(days=1) - timedelta(hours=1)
    overlap_values = df[overlap_date : overlap_end_date]
    overlap_avg = average(overlap_values['Bitcoin'])
    scaling = float(most_recent['Trend'] / overlap_avg)
    df['Bitcoin'] = df['Bitcoin'] * scaling

    # Parse by date and average the trend values
    df = df.groupby([df.index.date]).agg({'Bitcoin': ['mean']})

    # Remove the overlap item
    df = df[1:]

    return df

def get_interest_over_time(start_date):

    # The maximum for a timeframe for which we get daily data is 270.
    # Therefore we could go back 269 days. However, since there might
    # be issues when rescaling, e.g. zero entries, we should have an
    # overlap that does not consist of only one period. Therefore,
    # I limit the step size to 250. This leaves 19 periods for overlap.
    maxstep=269
    
    step = maxstep - overlap + 1
    dt = timedelta(days=step)
    time_fmt = '%Y-%m-%d'
    kw_list = ["Bitcoin"]

    ## FIRST RUN ##
    # Login to Google. Only need to run this once, the rest of requests will use the same session.
    pytrends = TrendReq(hl='en-US', tz=300)

    # Run the first time (if we want to start from today, otherwise we need to ask for an end_date as well
    # today = datetime(2019, 3, 1).date() 
    today = datetime.today().date()
    old_date = today

    # Go back in time
    new_date = today - dt #timedelta(hours=step)

    # Create new timeframe for which we download data
    timeframe = new_date.strftime(time_fmt)+' '+old_date.strftime(time_fmt)

    counter = 1
    pytrends.build_payload(kw_list=kw_list, timeframe = timeframe)
    interest_over_time_df = pytrends.interest_over_time()

    ## RUN ITERATIONS
    # Note this runs backwards from the most recent date back.
    while new_date > start_date:
        counter += 1
        ### Save the new date from the previous iteration.
        # Overlap == 1 would mean that we start where we
        # stopped on the iteration before, which gives us
        # indeed overlap == 1.
        old_date = new_date + timedelta(hours=overlap-1)

        ## Update the new date to take a step into the past
        # Since the timeframe that we can apply for daily data
        # is limited, we use step = maxstep - overlap instead of
        # maxstep.
        new_date = new_date - dt #timedelta(hours=step)
        # If we went past our start_date, use it instead
        if new_date < start_date:
            new_date = start_date

        # New timeframe
        timeframe = new_date.strftime(time_fmt)+' '+old_date.strftime(time_fmt)

        # Download data
        pytrends.build_payload(kw_list=kw_list, timeframe = timeframe)
        temp_df = pytrends.interest_over_time()

        if (temp_df.empty):
            raise ValueError('Google sent back an empty dataframe. Possibly there were no searches at all during the this period! Set start_date to a later date.')

        # Renormalize the dataset and drop last line
        for kw in kw_list:
            beg = new_date
            end = old_date - timedelta(hours=1)
            
            if temp_df[kw].iloc[-2] != 0:
                scaling = float(interest_over_time_df[kw].iloc[0])/temp_df[kw].iloc[-2]
            elif temp_df[kw].iloc[-1] != 0:
                scaling = float(interest_over_time_df[kw].iloc[1])/temp_df[kw].iloc[-1]
            else:
                print('Did not find non-zero overlap, set scaling to zero! Increase Overlap!')
                scaling = 0

            # Apply scaling
            temp_df.loc[beg:end,kw]=temp_df.loc[beg:end,kw]*scaling

        interest_over_time_df = pd.concat([temp_df[:-2],interest_over_time_df])
        time.sleep(1)

    return interest_over_time_df

def get_data_from_file(filename: str):
    data = pd.read_csv(filename) #, parse_dates=["date"])
    return data

def find_missing_dates(filename):
    data = get_data_from_file(filename)
    pandas_dates = data['date']
    # print("Dates:", pandas_dates)
    next_date = ''
    list = [date.fromisoformat(x) for x in pandas_dates]
    for current_date in list:
        if next_date != '' and next_date != current_date:
            print("Date:", current_date)
            print("Next Date:", next_date)
            break

        next_date = current_date + timedelta(days=1)

def get_chart(filename: str):
    import matplotlib.pyplot as plt
    import matplotlib.dates as dates

    data = get_data_from_file(filename)
    plt_dates = dates.date2num(data.date)
    yearFmt = dates.DateFormatter('%Y')
    ax = plt.subplot(111)
    ax.xaxis.set_major_formatter(yearFmt)
    plt.plot(plt_dates, data.Bitcoin, linestyle = 'solid')
    plt.xlabel("Year")
    plt.ylabel("Trend")
    plt.show()

if __name__ == "__main__":
    from google.cloud import datastore
    datastore_client = datastore.Client()
    run_daily_google_trends_update(datastore_client)
