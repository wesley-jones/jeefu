from flask import abort
from google.cloud import datastore
import pytz
import datetime
from utilities import constants

timezone = pytz.timezone('America/New_York')

def validate_cron_request(request):
    ''' Reference: https://partner-security.withgoogle.com/docs/appengine_tips.html '''
    host = request.headers.get('Host', None)
    header = request.headers.get('X-AppEngine-Cron', None)
    if not header and host != '127.0.0.1:8080':
        abort(403)

    return

def store_time(datastore_client, dt):
    entity = datastore.Entity(key=datastore_client.key('visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)

def fetch_times(datastore_client, limit):
    query = datastore_client.query(kind='visit')
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times

def get_most_recent_entity(datastore_client, kind):
  query = datastore_client.query(kind=kind)
  query.order = [constants.QUERY_ORDER_DATE_DESCENDING]
  most_recent = query.fetch(limit=1)

  return most_recent

def get_entities_starting_from(datastore_client, kind, start_date):
    query = datastore_client.query(kind=kind)
    query.order = [constants.QUERY_ORDER_DATE_DESCENDING]
    query.add_filter(constants.DATE, '>=', start_date)
    results = query.fetch()

    return results

def convert_cash_to_btc(cash_amount, btc_price):
    return cash_amount / btc_price

def convert_btc_to_cash(btc_amount, btc_price):
    '''This is the convert to cash function'''
    return btc_amount * btc_price

def get_rate_of_return(current_value, original_value):
    return ((current_value - original_value) / original_value) * 100

def get_today():
    today = datetime.datetime.now(timezone).date()
    return today

def get_yesterday():
    yesterday = get_today() - datetime.timedelta(days = 1)
    return yesterday

def save_to_datastore(datastore_client, kind, dictionaries):
    # Create your Google datastore entities
    count = len(dictionaries)
    entities = [datastore.Entity(key=datastore_client.key(kind)) for i in range(count)]

    # Add the data to the entities
    for entity, dictionary in zip(entities, dictionaries):
                entity.update(dictionary)

    # Save to google datastore. Max supported is 500 per call.
    batchsize = 500

    for i in range(0, len(entities), batchsize):
        batch = entities[i:i+batchsize]
        datastore_client.put_multi(batch)

