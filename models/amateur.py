# The Amateur oddly similar to myself

import datetime
from models import base

kind = 'Amateur'
alias = 'Mr. Jeefu'
description = 'I am an amateur'
image_url = 'https://www.w3schools.com/howto/img_avatar.png'
simulation_file = 'models/data/simulation_amateur.csv'
simulation_file_end_date = datetime.datetime(2021, 8, 20).date()
one_day = datetime.timedelta(days = 1)

def get_recommendations(datastore_client, start_date):
    recommendations = base.get_base_recommendations(datastore_client, kind, start_date, simulation_file, simulation_file_end_date)
    return recommendations
