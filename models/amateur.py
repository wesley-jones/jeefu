# The amateur makes similar decisions to me!!

from google.cloud import datastore
import datetime
import pytz
from utilities import utility, constants

kind = 'Amateur'
alias = 'The Amateur'
image_url = 'https://www.w3schools.com/howto/img_avatar.png'

def get_recommendations(datastore_client, start_date):
    loop_date = start_date

    recommendations = []
    one_day = datetime.timedelta(days = 1)

    while loop_date < utility.get_today():
        if loop_date == constants.HISTORICAL_START_DATE:
            recommendation = constants.BUY
        else:
            recommendation = constants.HOLD

        dictionary = {
            constants.DATE: loop_date,
            constants.RECOMMENDATION: recommendation
        }
        recommendations.append(dictionary)
        loop_date += one_day

    return recommendations

