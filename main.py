import datetime

from flask import Flask, render_template

from google.cloud import datastore

datastore_client = datastore.Client()


#########################################################
# Use this if you want to connect to a local datastore  #
#
# You will need to start your emulator with the following
# command:
#
# gcloud beta emulators datastore start --data-dir=. --project test --host-port "localhost:8001"
#
#########################################################
# import os
# if os.getenv('GAE_ENV', '').startswith('standard'):
#     # production
#     datastore_client = datastore.Client()
# else:
#     os.environ["DATASTORE_DATASET"] = "test"
#     os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8001"
#     os.environ["DATASTORE_EMULATOR_HOST_PATH"] = "localhost:8001/datastore"
#     os.environ["DATASTORE_HOST"] = "http://localhost:8001"
#     os.environ["DATASTORE_PROJECT_ID"] = "test"

#     datastore_client = datastore.Client(
#         project="test"
#     )
############################################################

app = Flask(__name__)

def store_time(dt):
    entity = datastore.Entity(key=datastore_client.key('visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)

def fetch_times(limit):
    query = datastore_client.query(kind='visit')
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times

@app.route('/')
def root():
    # Store the current access time in Datastore.
    store_time(datetime.datetime.now())

    # Fetch the most recent 10 access times from Datastore.
    times = fetch_times(10)
    print('times:', [x['timestamp'].strftime("%d/%m/%y %I:%M%p") for x in times])

    return render_template('index.html', times=times)


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
