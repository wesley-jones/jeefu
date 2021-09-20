import requests
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from utilities import utility, constants

nltk.download('vader_lexicon')

dataframe_filepath = 'jobs/data/news/news_data.pickle'

new_words = {
    'approaches': 1.0,
    'bear': -1.0,
    'bears': -1.0,
    'bet': 1.3,
    'blasts': 3.0,
    'break': 2.0,
    'breaking': 2.0,
    'breakout': 2.0,
    'breaks': 2.0,
    'broke': 2.0,
    'bull': 1.0,
    'bullish': 1.0,
    'bulls': 1.0,
    'buy': 2.0,
    'buying': 2.0,
    'buys': 2.0,
    'buy-the-dip': 3.0,
    'climbing': 2.0,
    'comeback': 2.0,
    'crackdown': -2.0,
    'crackdowns': -2.0,
    'declined': -2.0,
    'declining': -2.0,
    'exceed': 2.0,
    'exceeds': 2.0,
    'falter': -1.0,
    'falters': -3.0,
    # 'expands' already exists
    'fell': -1.0,
    'hard': 0.0,
    'jump': 1.0,
    'jumps': 1.0,
    'lucrative': 1.0,
    'moon': 3.0,
    'overbought': -2.0,
    'out-of-date': -2.0,
    'pullback': -3.4,
    'rally': 2.0,
    'rallies': 2.0,
    'recovery': 1.0,
    'retreats': -1.0,
    'rebound': 1.0,
    'rebounding': 1.0,
    'rebounds': 1.0,
    'rise': 2.0,
    'selloff': -2.0,
    'slides': -2.0,
    'slump': -2.0,
    'smash': 2.0,
    'smahes': 2.0,
    'soar': 2.0,
    'soars': 2.0,
    'surge': 3.0,
    'surging': 3.0,
    'surges': 3.0,
    'tax': -1.0,
    'topped': 1.0,
    # 'tops': 1.0, exists already
    'tumble': -3.0,
    'up': 2.0,
}

not_applicable_news_ids = {
    9184198666218655268
}

SIA = SentimentIntensityAnalyzer()
SIA.lexicon.update(new_words)

url = "https://custom-search.p.rapidapi.com/api/search/CustomNewsSearchAPIV3"

# Start date format: "2021-06-10T05:50:06"
# Filename format: 'jobs/data/news/data_95.json'
def get_news_from_api(start_date, filename):

    querystring = {
        "searchEngineId":"3530790746581235524",
        "q":"Bitcoin",
        "pageNumber": "1",
        # "fromPublishedDate":"2021-05-15T05:50:06",
        "pageSize": '100',
        "toPublishedDate": start_date
    }
    headers = {
        'x-rapidapi-key': utility.get_secret('RAPID_API_KEY'),
        'x-rapidapi-host': "custom-search.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    # print(data)
    print(data['totalCount'])
    print(len(data['value']))

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data

def open_json_file(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    return data


def get_sentiment_score(title, description):
    title_score = SIA.polarity_scores(title)['compound']
    description_score = SIA.polarity_scores(description)['compound']

    # Give the title's score more weight than the description score
    score = (title_score * .6) + (description_score * .4)

    # Return -1, 0, or 1
    if score < 0:
        score = -1
    if score > 0:
        score = 1

    return score

def get_news_list_from_csv_files(number_of_json_files=201):
    news_list = []

    for count in range(1, number_of_json_files + 1):
        data = open_json_file('jobs/data/news/data_' + str(count) + '.json')
        data_list = data['value']

        for item in data_list:
            dictionary = {
                # 'title': item['title'],
                'id': item['id'],
                'date_published': item['datePublished'],
                'sentiment': get_sentiment_score(item['title'], item['description'])
            }
            news_list.append(dictionary)

    return news_list

def save_to_disk():
    df = pd.DataFrame(get_news_list_from_csv_files())
    df = df.drop_duplicates(subset=['id'])
    df['Date'] = pd.to_datetime(df['date_published']).dt.date
    df.to_pickle(dataframe_filepath)

def load_from_disk():
    return pd.read_pickle(dataframe_filepath)

def group_by_day():
    df = load_from_disk()
    df = df.groupby('Date').agg({'id':'size', 'sentiment':'mean'}).rename(columns={'id':'count', 'sentiment':'avg_sentiment'}).reset_index()
    # print('No of rows:', len(df.index))
    pd.set_option("max_rows", None)
    # print(df.tail(160))

    data = pd.read_csv("models/data/basic_classification.csv", parse_dates=[constants.DATE])
    # print(data)
    sentiment_avg = df.set_index('Date')['avg_sentiment']
    sentiment_volume = df.set_index('Date')['count']
    # print(s)

    data['avg_sentiment'] = data['Date'].map(sentiment_avg)
    data['sentiment_volume'] = data['Date'].map(sentiment_volume)

    data['avg_sentiment'] = data['avg_sentiment'].fillna(method='ffill')
    data['sentiment_volume'] = data['sentiment_volume'].fillna(method='ffill')
    print(data)
    return data


def loop():
    date = "2018-08-31T06:51:00"
    starting_count = 174
    for count in range(1, 30):
        filename = 'jobs/data/news/data_' + str(starting_count + count) + '.json'
        print('Date:', date)
        print('File:', filename)
        data = get_news_from_api(date, filename)
        data_list = data['value']
        for item in data_list:
            date = item['datePublished']


if __name__ == "__main__":
    group_by_day()
