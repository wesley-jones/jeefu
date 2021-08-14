# Hodlers Never Sell!!

from google.cloud import datastore
import datetime
import pytz
from utilities import utility, constants

kind = 'Hodler'

def get_recommendations(datastore_client, start_date):
    loop_date = start_date

    recommendations = []
    one_day = datetime.timedelta(days = 1)

    while loop_date < utility.get_today():
        dictionary = {
            constants.DATE: loop_date,
            constants.RECOMMENDATION: 'Hold'
        }
        recommendations.append(dictionary)
        loop_date += one_day

    return recommendations

