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
    from sklearn.model_selection import train_test_split
    from joblib import dump, load
    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib.pyplot as plt
    from statsmodels.graphics.tsaplots import plot_acf
    from jobs import news

    # Load data
    data = pd.read_csv("models/data/basic_classification.csv", parse_dates=[constants.DATE])
    google_trends = pd.read_csv("jobs/data/google_trends_price_merged.csv")
    news_sentiment = pd.DataFrame(news.get_news_list())

    print(news_sentiment)

    # Preprocess the data
    # data['gtrends'] = google_trends['Google Trends']

    data['close_lag_1'] = data['Close'].shift(1)
    data['close_lag_2'] = data['Close'].shift(2)
    data['close_lag_3'] = data['Close'].shift(3)
    data['close_lag_4'] = data['Close'].shift(4)
    data['close_lag_5'] = data['Close'].shift(5)
    data['close_lag_6'] = data['Close'].shift(6)
    data['close_lag_7'] = data['Close'].shift(7)

    data['volume_lag_1'] = data['Volume'].shift(1)
    data['volume_lag_2'] = data['Volume'].shift(2)
    data['volume_lag_3'] = data['Volume'].shift(3)
    data['volume_lag_4'] = data['Volume'].shift(4)
    data['volume_lag_5'] = data['Volume'].shift(5)
    data['volume_lag_6'] = data['Volume'].shift(6)
    data['volume_lag_7'] = data['Volume'].shift(7)

    # data['gtrend_lag_1'] = data['gtrends'].shift(1)
    # data['gtrend_lag_2'] = data['gtrends'].shift(2)
    # data['gtrend_lag_3'] = data['gtrends'].shift(3)
    # data['gtrend_lag_4'] = data['gtrends'].shift(4)
    # data['gtrend_lag_5'] = data['gtrends'].shift(5)
    # data['gtrend_lag_6'] = data['gtrends'].shift(6)
    # data['gtrend_lag_7'] = data['gtrends'].shift(7)

    # plot_acf(data['Close'], lags=10)
    data['day_of_week'] = data[constants.DATE].dt.dayofweek
    # data['month_of_year'] = data[constants.DATE].dt.month

    data = data.drop('Date',axis=1)
    data = data.iloc[7: , :]
    print('Data:', data)

    # Split data into inputs/outputs
    X = data.loc[:, data.columns != 'Action']
    y = data['Action']

    # Split data into test/training
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, stratify=y)
    
    # Create Pipeline
    # pipe = make_pipeline(StandardScaler(), LinearSVC())
    # pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
    # pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3))
    pipe = make_pipeline(StandardScaler(), SVC(gamma='auto'))
    pipe.fit(X, y)
    dump(pipe, 'SupervisedModel.joblib')
    
    # pipe = load('SupervisedModel.joblib') 

    # Check the model's performance
    score = pipe.score(X_test, y_test)
    print('Score:', score)
    cm = confusion_matrix(y_test, pipe.predict(X_test))

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(cm)
    ax.grid(False)
    ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
    ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
    ax.set_ylim(1.5, -0.5)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha='center', va='center', color='red')
    plt.show()
    print(classification_report(y_test, pipe.predict(X_test)))
    
    
