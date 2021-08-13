from google.cloud import datastore
import datetime
import pytz
from jobs import marketday
from utilities import utility
from models import hodler


active_model_list = {
    hodler
}

def run_daily_model_updates(datastore_client):

    # Loop through each model
    for model in active_model_list:

        # Find the latest date in the datastore
        most_recent = utility.get_most_recent_entity(datastore_client, model.kind)

        # If its not up-to-date, then build all the missing dates up to yesterday.
        most_recent = list(most_recent)

        if most_recent:
            print('most_recent', model.kind + ":", most_recent[0])
            most_recent = most_recent[0]['Date'].date()
            start_date = most_recent + datetime.timedelta(days = 1)
        else:
            print('no days in datastore for entity', model.kind)
            start_date = datetime.datetime(2014, 9, 17).date()

        ### Retrieve required data for model
        # Query for market days that haven't been modeled
        # Validate market days
        # Loop thru market days and run model to get recommendation
        # 	calculate metrics
        # 	store entity
        # after loop save all entities to datastore
        if start_date < today:
            # Data should be all the data available starting with start_date
            data = model.get_model_data_starting_from(datastore_client, start_date)
            for d in data:
                recommendation = model.get_recommendation(datastore_client, d)
        else:
            pass

    return "Daily Model Updates have finished"
