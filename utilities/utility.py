from flask import abort
from google.cloud import datastore

def validate_cron_request(request):
    ''' Reference: https://partner-security.withgoogle.com/docs/appengine_tips.html '''
    header = request.headers.get('X-AppEngine-Cron', None)
    if not header:
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