from utilities import utility, constants
from jobs import marketday
import datetime
from models import model


one_day = datetime.timedelta(days = 1)

def build_bot_summary_context_by_day(datastore_client, requested_date):
    market_day = utility.get_entity_by_date(datastore_client, marketday.kind, requested_date)

    market_day = list(market_day)

    if market_day:
        market_day = market_day[0]
    else:
        market_day = {}

    model_list = []
    for active_model in model.active_model_list:
        entity = utility.get_entity_by_date(datastore_client, active_model.kind, requested_date)
        entity = list(entity)

        if entity:
            model_list.append(entity)

    dictionary = {
        'date': utility.custom_strftime(requested_date),
        'next_date': requested_date + one_day,
        'previous_date': requested_date - one_day,
        'market_day': market_day,
        'models': model_list
    }

    return dictionary

