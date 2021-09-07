from flask import Flask, render_template, request

from google.cloud import datastore

from utilities import utility
from jobs import marketday
from jobs import googletrends
from bots import bots
from web import webcontext


datastore_client = datastore.Client()
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

@app.route('/')
def root():
    # Get the web context for the date requested
    requested_date = request.args.get('date', default = utility.get_yesterday(), type = utility.to_date)
    print('Web | Requested Date:', requested_date)
    context = webcontext.build_bot_summary_context_by_day(datastore_client, requested_date)

    return render_template('index.html', context=context)

@app.route('/tasks/summary')
def cron_build_market_summary():
    utility.validate_cron_request(request=request)
    print('Starting Cron for Daily Market Summary')
    results = marketday.run_daily_market_summary_update(datastore_client)

    return results

@app.route('/tasks/gtrends')
def cron_build_gtrends():
    utility.validate_cron_request(request=request)
    print('Starting Cron for Google Trends')
    results = googletrends.run_daily_google_trends_update(datastore_client)

    return results

@app.route('/tasks/bots/daily_update')
def cron_run_daily_bot_updates():
    utility.validate_cron_request(request=request)
    print('Starting Cron for Daily Bot Updates')
    results = bots.run_daily_updates(datastore_client)
    print('Completed Cron for Daily Bot Updates')

    return results

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
