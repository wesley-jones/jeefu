from flask import abort
from google.cloud import datastore
import pytz
import datetime
from utilities import constants
import os

timezone = pytz.timezone('America/New_York')

def validate_cron_request(request):
    ''' Reference: https://partner-security.withgoogle.com/docs/appengine_tips.html '''
    host = request.headers.get('Host', None)
    header = request.headers.get('X-AppEngine-Cron', None)
    if not header and host != '127.0.0.1:8080':
        abort(403)

    return

def get_all_entities_by_kind(datastore_client, kind, ascending=True):
    query = datastore_client.query(kind=kind)
    query.order = [constants.QUERY_ORDER_DATE_ASCENDING if ascending else constants.QUERY_ORDER_DATE_DESCENDING]
    results = query.fetch()
    
    return results

def get_most_recent_entity(datastore_client, kind):
  query = datastore_client.query(kind=kind)
  query.order = [constants.QUERY_ORDER_DATE_DESCENDING]
  most_recent = query.fetch(limit=1)

  return most_recent

def get_first_entity(datastore_client, kind):
  query = datastore_client.query(kind=kind)
  query.order = [constants.QUERY_ORDER_DATE_ASCENDING]
  first_entity = query.fetch(limit=1)

  return first_entity

def get_entities_starting_from(datastore_client, kind, start_date):

    if isinstance(start_date, datetime.date):
        start_date = cast_date_to_datetime(start_date)
    query = datastore_client.query(kind=kind)
    query.order = [constants.QUERY_ORDER_DATE_ASCENDING]
    query.add_filter(constants.DATE, '>=', start_date)
    results = query.fetch()

    return results

def get_entity_by_date(datastore_client, kind, requested_date):

    if isinstance(requested_date, datetime.date):
        requested_date = cast_date_to_datetime(requested_date)
    query = datastore_client.query(kind=kind)
    query.add_filter(constants.DATE, '=', requested_date)
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

def to_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

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

def cast_date_to_datetime(your_date):
    new_datetime = datetime.datetime.combine(your_date, datetime.datetime.min.time())
    return new_datetime

# Pass in a datetime and get output like the following: August 15th, 2021
def custom_strftime(t):
    format = '%B {S}, %Y'
    suffix = 'th' if 11<=t.day<=13 else {1:'st',2:'nd',3:'rd'}.get(t.day%10, 'th')
    return t.strftime(format).replace('{S}', str(t.day) + suffix)

def pluralize(word, length):
    if length > 1:
        word = word + 's'
    
    return word

def calculate_average_from_list(list_of_days):
    if list_of_days:
        if sum(list_of_days) == 0:
            average = 0
        else:
            average = sum(list_of_days) / len(list_of_days)
    else:
        average = 0

    return average

def get_secret(secret_name):
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    project_id = 'gcp-test-322220' if project_id == None else project_id

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Return the secret payload.
    #
    # WARNING: Do not copy, store, or print the secret!
    secret = response.payload.data.decode("UTF-8")
    return secret
