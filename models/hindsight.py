# Hindsight can go back in time!!

from google.cloud import datastore
import datetime
import pytz
from utilities import utility, constants
import pandas as pd

kind = 'Hindsight'
alias = 'Mr. Hindsight'
image_url = 'https://www.w3schools.com/howto/img_avatar.png'
simulation_file = 'models/data/simulation_3_optimal.csv'
simulation_file_end_date = datetime.datetime(2021, 7, 9).date()
one_day = datetime.timedelta(days = 1)


def get_recommendations(datastore_client, start_date):
    loop_date = start_date
    recommendations = []
    data = pd.read_csv(simulation_file)

    if start_date > simulation_file_end_date:
        recommendations = set_recommendations_to_hold(start_date, recommendations)

    else:
        loop_date = start_date
        for index, row in data.iterrows():
            row_date = datetime.datetime.strptime(row[constants.DATE], '%m/%d/%y').date()
            if row_date < loop_date:
                # Do nothing. Go to next row.
                pass
            elif row_date == loop_date:
                # Get recomendation
                dictionary = {
                    constants.DATE: loop_date,
                    constants.RECOMMENDATION: row[constants.ACTION]
                }
                recommendations.append(dictionary)
                loop_date += one_day
            else:
                # Data is missing a day
                print(
                    'Missing',
                    kind,
                    'data for',
                    loop_date
                )
                return recommendations

        recommendations = set_recommendations_to_hold(loop_date, recommendations)

    return recommendations

def set_recommendations_to_hold(start_date, recommendations):
    loop_date = start_date
    while loop_date < utility.get_today():
        dictionary = {
            constants.DATE: loop_date,
            constants.RECOMMENDATION: constants.HOLD
        }
        recommendations.append(dictionary)
        loop_date += one_day

    return recommendations
