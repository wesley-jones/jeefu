import datetime
from utilities import utility, constants
from models import hodler
from jobs import marketday


'''
Every model should implement the following variables:
    kind
        the google store entity name

Every model should implement the following functions:
    get_recommendations(datastore_client, data)
        Should be list of dictionary with two fields
        Date and Recommendation
        Example:
        {
            Date: '2-18-2021 00:00:00,
            Recommendation: 'Hold'
        }

'''

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
            print('most_recent', model.kind + ":", most_recent[0][constants.DATE])
            most_recent = most_recent[0]['Date'].date()
            start_date = most_recent + datetime.timedelta(days = 1)
        else:
            print('no days in datastore for entity', model.kind)
            start_date = datetime.datetime(2014, 9, 17).date()

        today = utility.get_today()

        if start_date < today:

            # Get the recommendations list
            recommendations = model.get_recommendations(datastore_client, start_date)

            # Make sure the dates line up
            if start_date != recommendations[0][constants.DATE]:
                print('Start dates do not align for' + model.kind)
                return []

            # Calculate the daily metrics
            dictionaries = calculate_daily_metrics(datastore_client, start_date, model, recommendations)

            # Save to google datastore
            utility.save_to_datastore(datastore_client, model.kind, dictionaries)

        else:
            print(model.kind, 'is up-to-date!')

    # End for loop

    return "Daily Model Updates have finished"

# Returns a list of dictionaries
def calculate_daily_metrics(datastore_client, start_date, model, recommendations):

    # Get the latest data in the model's datastore
    most_recent = utility.get_most_recent_entity(datastore_client, model.kind)

    most_recent = list(most_recent)

    # Previous days already exist for this model
    if most_recent:
        if most_recent[0].Date != start_date:
            print("Most recent date doesn't match with recommendations for " + model.kind)
            return []

        previous_day_model = most_recent

    # First time this model has ran
    else:
        cash_balance = constants.HISTORICAL_STARTING_CASH_BALANCE
        previous_day_model = populate_default_model()

    market_days = utility.get_entities_starting_from(datastore_client, marketday.kind, start_date)

    dictionaries = []
    one_day = 1

    for recommendation in recommendations:

        try:
            market_day = next(market_days)
        except StopIteration as e:
            print('Mismatch with market days and recommendations for', model.kind)
            return dictionaries

        if recommendation[constants.DATE] != market_day[constants.DATE].date():
            print('Mismatch with dates of market days and recommendations for', model.kind)
            return dictionaries

        # Reset the variables
        action = ''
        cash_balance = previous_day_model[constants.CASH_BALANCE]
        btc_balance = previous_day_model[constants.BTC_BALANCE]
        recommendation_value = recommendation[constants.RECOMMENDATION]
        close_price = market_day[constants.CLOSE_PRICE]
        previous_transaction_close_price = previous_day_model[constants.PREVIOUS_TRANSACTION_CLOSE_PRICE]
        list_returns_per_buy = previous_day_model[constants.LIST_RETURNS_PER_BUY]
        list_returns_per_sell = previous_day_model[constants.LIST_RETURNS_PER_SELL]
        consecutive_days_holding_cash = previous_day_model[constants.CONSECUTIVE_DAYS_HOLDING_CASH]
        consecutive_days_holding_btc = previous_day_model[constants.CONSECUTIVE_DAYS_HOLDING_BTC]
        list_consecutive_days_holding_cash = previous_day_model[constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH]
        list_consecutive_days_holding_btc = previous_day_model[constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC]
        rate_of_return = 0

        # Action = Buy
        if recommendation_value == constants.BUY and cash_balance > 0:
            # Buy Bitcoin
            action = constants.BUY
            amount_to_buy = utility.convert_cash_to_btc(cash_balance, close_price)
            if previous_transaction_close_price > 0:
                rate_of_return = utility.get_rate_of_return(previous_transaction_close_price, close_price)
                list_returns_per_buy.append(rate_of_return)
            log_transaction(
                model = model,
                date = recommendation[constants.DATE],
                transaction_type = constants.BUY,
                rate_of_return = rate_of_return,
                btc_amount = amount_to_buy,
                cash_amount = cash_balance,
                close_price = close_price
            )
            btc_balance = btc_balance + amount_to_buy
            cash_balance = 0

            list_consecutive_days_holding_cash.append(consecutive_days_holding_cash + one_day)
            consecutive_days_holding_cash = 0

            previous_transaction_close_price = close_price

        # Action = Sell
        elif recommendation_value == constants.SELL and btc_balance > 0:
            # Sell Bitcoin
            action = constants.SELL
            cash_to_receive = utility.convert_btc_to_cash(btc_balance, close_price)
            if previous_transaction_close_price > 0:
                rate_of_return = utility.get_rate_of_return(close_price, previous_transaction_close_price)
                list_returns_per_sell.append(rate_of_return)

            log_transaction(
                model = model,
                date=recommendation[constants.DATE],
                transaction_type=constants.SELL,
                rate_of_return=rate_of_return,
                btc_amount=btc_balance,
                cash_amount=cash_to_receive,
                close_price=close_price
            )
            cash_balance = cash_balance + cash_to_receive
            btc_balance = 0

            list_consecutive_days_holding_btc.append(consecutive_days_holding_btc + one_day)
            consecutive_days_holding_btc = 0

            previous_transaction_close_price = close_price

        # Action = Hold
        else:
            action = constants.HOLD

            if cash_balance > 0:
                consecutive_days_holding_cash += 1
            elif btc_balance > 0:
                consecutive_days_holding_btc += 1

        final_balance_in_cash = cash_balance + utility.convert_btc_to_cash(btc_balance, close_price)

        dictionary = {
            constants.DATE: utility.cast_date_to_datetime(recommendation[constants.DATE]),
            constants.ACTION: action,
            constants.RECOMMENDATION: recommendation_value,
            constants.CASH_BALANCE: cash_balance,
            constants.BTC_BALANCE: btc_balance,
            constants.AVG_DAYS_HOLDING_BTC: get_average_from_list(list_consecutive_days_holding_btc),
            constants.AVG_DAYS_HOLDING_CASH: get_average_from_list(list_consecutive_days_holding_cash),
            constants.TOTAL_DAYS_HOLDING_CASH: sum(list_consecutive_days_holding_cash),
            constants.TOTAL_DAYS_HOLDING_BTC: sum(list_consecutive_days_holding_btc),
            constants.AVG_RETURN_ON_BUYS: get_average_from_list(list_returns_per_buy),
            constants.AVG_RETURN_ON_SELLS: get_average_from_list(list_returns_per_sell),
            constants.NET_PROFIT_IN_CASH: final_balance_in_cash - constants.HISTORICAL_STARTING_CASH_BALANCE,
            constants.AVG_RETURN_PER_TRANSACTION: get_average_from_list(list_returns_per_buy + list_returns_per_sell),
            constants.TOTAL_RETURN: utility.get_rate_of_return(final_balance_in_cash, constants.HISTORICAL_STARTING_CASH_BALANCE),
            constants.PREVIOUS_TRANSACTION_CLOSE_PRICE: previous_transaction_close_price,
            constants.CONSECUTIVE_DAYS_HOLDING_CASH: consecutive_days_holding_cash,
            constants.CONSECUTIVE_DAYS_HOLDING_BTC: consecutive_days_holding_btc,
            constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH: list_consecutive_days_holding_cash,
            constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC: list_consecutive_days_holding_btc,
            constants.LIST_RETURNS_PER_BUY: list_returns_per_buy,
            constants.LIST_RETURNS_PER_SELL: list_returns_per_sell,
        }

        if recommendation[constants.DATE] > datetime.datetime(2021, 8, 11).date():
            print(dictionary)

        dictionaries.append(dictionary)
        previous_day_model = dictionary
        
    return dictionaries

def log_transaction(model, date, transaction_type, rate_of_return, btc_amount, cash_amount, close_price):
    print(
        'Transaction for',
        model.kind,
        '|',
        date,
        '|',
        transaction_type,
        f'({rate_of_return:+,.0f}%)',
        '|',
        f'{btc_amount:,.1f} BTC for ${cash_amount:,.0f}'
        if transaction_type == 'Sell'
        else f'{btc_amount:,.1f} BTC for ${cash_amount:,.0f}',
        '|',
        f'Close price: ${close_price:,.0f}'
    )

def populate_default_model():
    dictionary = {
        constants.DATE: constants.HISTORICAL_START_DATE - datetime.timedelta(days = 1),
        constants.ACTION: constants.HOLD,
        constants.RECOMMENDATION: constants.HOLD,
        constants.CASH_BALANCE: constants.HISTORICAL_STARTING_CASH_BALANCE,
        constants.BTC_BALANCE: 0,
        constants.AVG_DAYS_HOLDING_BTC: 0,
        constants.AVG_DAYS_HOLDING_CASH: 0,
        constants.TOTAL_DAYS_HOLDING_CASH: 0,
        constants.TOTAL_DAYS_HOLDING_BTC: 0,
        constants.AVG_RETURN_ON_BUYS: 0,
        constants.AVG_RETURN_ON_SELLS: 0,
        constants.NET_PROFIT_IN_CASH: 0,
        constants.AVG_RETURN_PER_TRANSACTION: 0,
        constants.TOTAL_RETURN: 0,
        constants.PREVIOUS_TRANSACTION_CLOSE_PRICE: 0,
        constants.CONSECUTIVE_DAYS_HOLDING_CASH: 0,
        constants.CONSECUTIVE_DAYS_HOLDING_BTC: 0,
        constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH: [],
        constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC: [],
        constants.LIST_RETURNS_PER_BUY: [],
        constants.LIST_RETURNS_PER_SELL: []
    }

    return dictionary

def get_average_from_list(list_of_days):
    if sum(list_of_days) == 0:
        average = 0
    else:
        average = sum(list_of_days) / len(list_of_days)
    return average
