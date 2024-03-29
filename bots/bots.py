import datetime
from utilities import utility, constants
from bots import hodler, hindsight, amateur
from jobs import marketday


'''
Every bot should implement the following variables:
    kind
        the google store entity name
    alias
        the name shown on the website
    image_url
        the avatar shown on the website

Every bot should implement the following functions:
    get_recommendations(datastore_client, start_date)
        Should be list of dictionary with two fields
        Date and Recommendation
        Example:
        {
            Date: '2-18-2021 00:00:00,
            Recommendation: 'Hold'
        }

'''

active_bot_list = {
    hodler,
    hindsight,
    amateur
}

def run_daily_updates(datastore_client):

    has_error = False

    # Loop through each bot
    for bot in active_bot_list:

        # Find the latest date in the datastore
        most_recent = utility.get_most_recent_entity(datastore_client, bot.kind)

        # If its not up-to-date, then build all the missing dates up to yesterday.
        most_recent = list(most_recent)

        if most_recent:
            most_recent = most_recent[0]['Date'].date()
            start_date = most_recent + datetime.timedelta(days = 1)
        else:
            print('No days in datastore for entity', bot.kind)
            start_date = datetime.datetime(2014, 9, 17).date()

        today = utility.get_today()

        if start_date < today:

            # Get the recommendations list
            recommendations = bot.get_recommendations(datastore_client, start_date)

            # Make sure the dates line up
            if start_date != recommendations[0][constants.DATE]:
                print('Start dates do not align for', bot.kind)
                recommendations = []
                has_error = True

            # Calculate the daily metrics
            dictionaries = calculate_daily_metrics(datastore_client, start_date, bot, recommendations)

            print(
                "Adding",
                len(dictionaries),
                utility.pluralize('record', len(dictionaries)),
                "to",
                bot.kind
            )
            # Save to google datastore
            utility.save_to_datastore(datastore_client, bot.kind, dictionaries)

        else:
            print(bot.kind, 'is up-to-date!')

    # End for loop

    return "Daily Bot Updates have finished with errors" if has_error else "Daily Bot Updates have finished"

# Returns a list of dictionaries
def calculate_daily_metrics(datastore_client, start_date, bot, recommendations):

    # Get the latest data in the bot's datastore
    most_recent = utility.get_most_recent_entity(datastore_client, bot.kind)

    most_recent = list(most_recent)

    # Previous days already exist for this bot
    if most_recent:
        most_recent = most_recent[0]
        if most_recent[constants.DATE].date() != start_date - datetime.timedelta(days = 1):
            print(
                "Most recent date",
                most_recent[constants.DATE].date(),
                "doesn't match with the day before the first recommendation date",
                start_date - datetime.timedelta(days = 1),
                "for",
                bot.kind
            )
            return []

        previous_day_bot = most_recent

    # First time this Bot has ran
    else:
        cash_balance = constants.HISTORICAL_STARTING_CASH_BALANCE
        previous_day_bot = populate_default_bot()

    market_days = utility.get_entities_starting_from(datastore_client, marketday.kind, start_date)

    dictionaries = []
    one_day = 1

    for recommendation in recommendations:

        try:
            market_day = next(market_days)
        except StopIteration as e:
            print('Mismatch with market days and recommendations for', bot.kind)
            return dictionaries

        verify_previous_bot_date = (previous_day_bot[constants.DATE] + datetime.timedelta(days = 1)).date()
        if (
            recommendation[constants.DATE] != market_day[constants.DATE].date()
            or verify_previous_bot_date != market_day[constants.DATE].date()
        ):
            print(
                'Mismatch with dates for', 
                bot.kind,
                "\n",
                "Recommendation:",
                recommendation[constants.DATE],
                "\n",
                "Market day:",
                market_day[constants.DATE].date(),
                "\n",
                "Previous bot date:",
                verify_previous_bot_date
            )
            return dictionaries

        # Reset the variables
        action = ''
        cash_balance = previous_day_bot[constants.CASH_BALANCE]
        btc_balance = previous_day_bot[constants.BTC_BALANCE]
        recommendation_value = recommendation[constants.RECOMMENDATION]
        close_price = market_day[constants.CLOSE_PRICE]
        previous_transaction_close_price = previous_day_bot[constants.PREVIOUS_TRANSACTION_CLOSE_PRICE]
        list_returns_per_buy = previous_day_bot[constants.LIST_RETURNS_PER_BUY].copy()
        list_returns_per_sell = previous_day_bot[constants.LIST_RETURNS_PER_SELL].copy()
        consecutive_days_holding_cash = previous_day_bot[constants.CONSECUTIVE_DAYS_HOLDING_CASH]
        consecutive_days_holding_btc = previous_day_bot[constants.CONSECUTIVE_DAYS_HOLDING_BTC]
        list_consecutive_days_holding_cash = previous_day_bot[constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH].copy()
        list_consecutive_days_holding_btc = previous_day_bot[constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC].copy()
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
                bot = bot,
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
                bot = bot,
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
            constants.DATE: market_day[constants.DATE],
            constants.ACTION: action,
            constants.RECOMMENDATION: recommendation_value,
            constants.CASH_BALANCE: cash_balance,
            constants.BTC_BALANCE: btc_balance,
            constants.PREVIOUS_TRANSACTION_CLOSE_PRICE: previous_transaction_close_price,
            constants.CONSECUTIVE_DAYS_HOLDING_CASH: consecutive_days_holding_cash,
            constants.CONSECUTIVE_DAYS_HOLDING_BTC: consecutive_days_holding_btc,
            constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH: list_consecutive_days_holding_cash,
            constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC: list_consecutive_days_holding_btc,
            constants.LIST_RETURNS_PER_BUY: list_returns_per_buy,
            constants.LIST_RETURNS_PER_SELL: list_returns_per_sell,
        }

        dictionaries.append(dictionary)
        previous_day_bot = dictionary
        
    return dictionaries

def log_transaction(bot, date, transaction_type, rate_of_return, btc_amount, cash_amount, close_price):
    print(
        'Transaction for',
        bot.kind,
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

def populate_default_bot():
    dictionary = {
        constants.DATE: utility.cast_date_to_datetime(constants.HISTORICAL_START_DATE - datetime.timedelta(days = 1)),
        constants.ACTION: constants.HOLD,
        constants.RECOMMENDATION: constants.HOLD,
        constants.CASH_BALANCE: constants.HISTORICAL_STARTING_CASH_BALANCE,
        constants.BTC_BALANCE: 0,
        constants.PREVIOUS_TRANSACTION_CLOSE_PRICE: 0,
        constants.CONSECUTIVE_DAYS_HOLDING_CASH: 0,
        constants.CONSECUTIVE_DAYS_HOLDING_BTC: 0,
        constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH: [],
        constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC: [],
        constants.LIST_RETURNS_PER_BUY: [],
        constants.LIST_RETURNS_PER_SELL: []
    }

    return dictionary
