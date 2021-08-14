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
            print('most_recent', model.kind + ":", most_recent[0])
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
            # dictionaries = calculate_daily_metrics(datastore_client, model, recommendations)

            for x in recommendations:
                # Cast dates to datetimes
                x[constants.DATE] = datetime.datetime.combine(
                    x[constants.DATE], 
                    datetime.datetime.min.time()
                )
                print(x[constants.DATE])

            # Save to google datastore
            utility.save_to_datastore(datastore_client, model.kind, recommendations)

    # End for loop

    return "Daily Model Updates have finished"

def calculate_daily_metrics(datastore_client, start_date, model, recommendations):
    ''' 
    Returns a list of dictionaries
    Example structure
    {
        Date: '2021-10-10 00:00:00', (save)
        Recommendation: 'Hold', (save)
        Action: 'Sell', (save)
        - Total Return: .44, (need final and starting balance)
        Cash Balance: 2,222.44, (save)
        BTC Balance: 0, (save)
        Avg Days Holding Cash: 23, (save)
        Avg Days Holding BTC: 72, (save)
        Avg Return per Buy:  .43, (save)
        Avg Return per Sell: .44 (save)
    }
    '''


    # Get the latest data in the model datastore
    most_recent = utility.get_most_recent_entity(datastore_client, model.kind)

    most_recent = list(most_recent)

    if most_recent:
        if most_recent[0].Date != start_date:
            print("Most recent date doesn't match with recommendations for " + model.kind)
            return []

        # set previous
    else:
        # set previous
        starting_cash_balance = 458
        cash_balance = starting_cash_balance
        btc_balance = most_recent.btc_balance
        final_closing_price = 0.0
        start_date_str = None
        end_date_str = None
        days_holding_btc: int = 0
        days_holding_cash: int = 0
        avg_days_holding_btc_list = []
        avg_days_holding_cash_list = []
        avg_days_holding_btc_counter: float = 0
        avg_days_holding_cash_counter: float = 0
        previous_transaction_close_price: float = 0
        rate_of_return_sell_list = []
        rate_of_return_buy_list = []
        rate_of_return = 0

    market_days = get_entities_starting_from(datastore_client, marketday.kind, start_date)

    # ensure market days list is same size as recommendations

    dictionaries = []

    for market_day, recommendation in zip(market_days, recommendations):
        # ensure the dates match

        if recommendation[constants.ACTION] == constants.BUY and cash_balance > 0:
            # Buy Bitcoin
            amount_to_purchase = utility.convert_cash_to_btc(cash_balance, market_day['Close'])
            if previous_transaction_close_price > 0:
                rate_of_return = utility.get_rate_of_return(previous_transaction_close_price, row['Close'])
                rate_of_return_buy_list.append(rate_of_return)
            log_transaction(
                date=row['Date'],
                transaction_type = 'Buy',
                rate_of_return=rate_of_return,
                btc_amount=amount_to_purchase,
                cash_amount=cash_balance,
                close_price=row['Close']
            )
            btc_balance += amount_to_purchase
            cash_balance = 0
            if avg_days_holding_cash_counter > 0:
                avg_days_holding_cash_list.append(avg_days_holding_cash_counter)
                avg_days_holding_cash_counter = 0
            if previous_transaction_close_price > 0:
                pass
            previous_transaction_close_price = float(row['Close'])

        if row[constants.ACTION] == constants.SELL and btc_balance > 0:
            # Sell Bitcoin
            cash_to_receive = utility.convert_btc_to_cash(btc_balance, row['Close'])
            if previous_transaction_close_price > 0:
                rate_of_return = utility.get_rate_of_return(row['Close'], previous_transaction_close_price)
                rate_of_return_sell_list.append(rate_of_return)

            log_transaction(
                date=row['Date'],
                transaction_type='Sell',
                rate_of_return=rate_of_return,
                btc_amount=btc_balance,
                cash_amount=cash_to_receive,
                close_price=row['Close']
            )
            cash_balance += cash_to_receive
            btc_balance = 0
            if avg_days_holding_btc_counter > 0:
                avg_days_holding_btc_list.append(avg_days_holding_btc_counter)
                avg_days_holding_btc_counter = 0
            if previous_transaction_close_price > 0:
                pass
            previous_transaction_close_price = float(row['Close'])
        
        if row[constants.ACTION] == constants.HOLD:
            dictionary = {
                constants.DATE: recommendation.Date,
                constants.RECOMMENDATION: recommendation.recommendation,
                constants.ACTION: constants.HOLD
            }

        dictionaries.append(dictionary)
        
    return dictionaries



def log_transaction(date, transaction_type, rate_of_return, btc_amount, cash_amount, close_price):
    # logging.info(' '.join([
    #     ' ',
    #     date,
    #     '|',
    #     transaction_type,
    #     f'({rate_of_return:+,.0f}%)',
    #     '|',
    #     f'{btc_amount:,.1f} BTC for ${cash_amount:,.0f}' 
    #     if transaction_type == 'Sell' 
    #     else f'{btc_amount:,.1f} BTC for ${cash_amount:,.0f}',
    #     '|',
    #     f'Close price: ${close_price:,.0f}'
    # ]))
    return





