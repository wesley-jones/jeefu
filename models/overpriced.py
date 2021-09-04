# Trained by supervised learning!!

import datetime
from models import base
from utilities import constants

kind = 'Supervised'
alias = 'The Apprentice'
description = 'I am taught thru supervised learning'
image_url = 'https://www.w3schools.com/howto/img_avatar.png'
# simulation_file = 'models/data/simulation_3_optimal.csv'
# simulation_file_end_date = datetime.datetime(2021, 8, 20).date()
one_day = datetime.timedelta(days = 1)

def get_recommendations(datastore_client, start_date):
    # Need to call the supervised learning algorithm
    recommendations = []
    
    
    return recommendations


if __name__ == "__main__":
    import pandas as pd
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import LinearSVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn import svm
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from joblib import dump, load
    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib.pyplot as plt
    from statsmodels.graphics.tsaplots import plot_acf
    from jobs import news
    import numpy as np

    # Load data
    data = pd.read_csv("models/data/basic_classification_spike_sells.csv", parse_dates=[constants.DATE])
    google_trends = pd.read_csv("jobs/data/google_trends_price_merged.csv")
    news_sentiment = news.group_by_day()

    # Preprocess the data
    # data['sentiment_volume'] = news_sentiment['sentiment_volume']
    # data['sentiment_volume_lag_1'] = data['sentiment_volume'].shift(1)
    # data['sentiment_volume_lag_2'] = data['sentiment_volume'].shift(2)
    # data['sentiment_volume_lag_3'] = data['sentiment_volume'].shift(3)
    

    # data['sentiment'] = news_sentiment['avg_sentiment']
    # data['sentiment_lag_1'] = data['sentiment'].shift(1)
    # data['sentiment_lag_2'] = data['sentiment'].shift(2)
    # data['sentiment_lag_3'] = data['sentiment'].shift(3)
    # data['sentiment_lag_4'] = data['sentiment'].shift(4)
    # data['sentiment_lag_5'] = data['sentiment'].shift(5)
    # data['sentiment_lag_6'] = data['sentiment'].shift(6)
    # data['sentiment_lag_7'] = data['sentiment'].shift(7)
    # data['sentiment_lag_8'] = data['sentiment'].shift(8)
    # data['sentiment_lag_9'] = data['sentiment'].shift(9)
    # data['sentiment_lag_10'] = data['sentiment'].shift(10)
    # data['sentiment_lag_11'] = data['sentiment'].shift(11)
    # data['sentiment_lag_12'] = data['sentiment'].shift(12)


    # data['close_SMA_2'] = data['Close'].rolling(window=2).mean()
    data['close_SMA_3'] = data['Close'].rolling(window=3).mean()
    data['close_SMA_4'] = data['Close'].rolling(window=4).mean()
    data['close_SMA_5'] = data['Close'].rolling(window=5).mean()
    # data['close_SMA_6'] = data['Close'].rolling(window=6).mean()
    # data['close_SMA_7'] = data['Close'].rolling(window=7).mean()
    # data['close_SMA_8'] = data['Close'].rolling(window=8).mean()
    # data['close_SMA_9'] = data['Close'].rolling(window=9).mean()
    # data['close_SMA_10'] = data['Close'].rolling(window=10).mean()
    # data['close_SMA_11'] = data['Close'].rolling(window=11).mean()
    # data['close_SMA_12'] = data['Close'].rolling(window=12).mean()
    # data['close_SMA_13'] = data['Close'].rolling(window=13).mean()
    # data['close_SMA_14'] = data['Close'].rolling(window=14).mean()
    # data['close_SMA_30'] = data['Close'].rolling(window=30).mean()


    data['close_lag_1'] = data['Close'].shift(1)
    data['close_lag_2'] = data['Close'].shift(2)
    data['close_lag_3'] = data['Close'].shift(3)
    # data['close_lag_4'] = data['Close'].shift(4)
    # data['close_lag_5'] = data['Close'].shift(5)
    # data['close_lag_6'] = data['Close'].shift(6)
    # data['close_lag_7'] = data['Close'].shift(7)

    # data['volume_lag_1'] = data['Volume'].shift(1)
    # data['volume_lag_2'] = data['Volume'].shift(2)
    # data['volume_lag_3'] = data['Volume'].shift(3)
    # data['volume_lag_4'] = data['Volume'].shift(4)
    # data['volume_lag_5'] = data['Volume'].shift(5)
    # data['volume_lag_6'] = data['Volume'].shift(6)
    # data['volume_lag_7'] = data['Volume'].shift(7)

    data['gtrends'] = google_trends['Google Trends']
    data['gtrend_lag_1'] = data['gtrends'].shift(1)
    data['gtrend_lag_2'] = data['gtrends'].shift(2)
    data['gtrend_lag_3'] = data['gtrends'].shift(3)
    data['gtrend_lag_4'] = data['gtrends'].shift(4)
    data['gtrend_lag_5'] = data['gtrends'].shift(5)
    data['gtrend_lag_6'] = data['gtrends'].shift(6)
    data['gtrend_lag_7'] = data['gtrends'].shift(7)
    data['gtrend_lag_8'] = data['gtrends'].shift(8)
    data['gtrend_lag_9'] = data['gtrends'].shift(9)
    data['gtrend_lag_10'] = data['gtrends'].shift(10)
    data['gtrend_lag_11'] = data['gtrends'].shift(11)
    data['gtrend_lag_12'] = data['gtrends'].shift(12)
    data['gtrend_lag_13'] = data['gtrends'].shift(13)
    data['gtrend_lag_14'] = data['gtrends'].shift(14)
    data['gtrend_lag_15'] = data['gtrends'].shift(15)
    data['gtrend_lag_16'] = data['gtrends'].shift(16)
    data['gtrend_lag_17'] = data['gtrends'].shift(17)
    data['gtrend_lag_18'] = data['gtrends'].shift(18)
    data['gtrend_lag_19'] = data['gtrends'].shift(19)
    data['gtrend_lag_20'] = data['gtrends'].shift(20)

    # plot_acf(data['Close'], lags=10)
    # data['day_of_week'] = data[constants.DATE].dt.dayofweek
    data['month_of_year'] = data[constants.DATE].dt.month

    # data.to_csv('supervised.csv')

    data = data.drop('Date',axis=1)
    # data = data.drop('Volume',axis=1)
    data = data.iloc[20: , :]
    # print('Data:', data)

    # Split data into inputs/outputs
    X = data.loc[:, data.columns != 'Action']
    y = data['Action']

    # Split data into test/training
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=88, stratify=y)

    # Create Pipeline
    # pipe = make_pipeline(StandardScaler(), LinearSVC())
    # pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))

    pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=2, weights='distance', metric='manhattan'))

    # pipe = make_pipeline(StandardScaler(), RandomForestClassifier(max_depth=100, criterion='entropy', n_estimators=10))


    
    # pipe = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    # pipe = make_pipeline(StandardScaler(), svm.NuSVC(nu=.013))
    pipe.fit(X_train, y_train)


    predictions = pipe.predict(X_test)
    for input, prediction, label in zip(X_test['Close'], predictions, y_test):
        if prediction != label:
            print(input, 'has been classified as ', prediction, 'and should be ', label)
        

    
    # dump(pipe, 'SupervisedModel.joblib')
    # pipe = load('SupervisedModel.joblib') 

    # Check the model's performance
    # score = pipe.score(X_test, y_test)
    
    cm = confusion_matrix(y_test, pipe.predict(X_test))
    print('Confusion Matrix:\n', cm)

    # fig, ax = plt.subplots(figsize=(8, 8))
    # ax.imshow(cm)
    # ax.grid(False)
    # ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
    # ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
    # ax.set_ylim(1.5, -0.5)
    # for i in range(2):
    #     for j in range(2):
    #         ax.text(j, i, cm[i, j], ha='center', va='center', color='red')
    # plt.show()
    print(classification_report(y_test, pipe.predict(X_test)))
    # print('Score:', score)

    print('Training:', pipe.score(X_train, y_train))
    print('Testing:', pipe.score(X_test, y_test))




    
    
    
