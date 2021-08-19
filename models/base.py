# Base model used for csv based models

import datetime
from utilities import utility, constants
import pandas as pd

one_day = datetime.timedelta(days = 1)

def get_base_recommendations(datastore_client, kind, start_date, simulation_file, simulation_file_end_date):
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
