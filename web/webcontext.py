from utilities import utility, constants
from jobs import marketday
import datetime
from models import model
from dateutil.relativedelta import relativedelta


one_day = datetime.timedelta(days = 1)

def build_bot_summary_context_by_day(datastore_client, requested_date):
    market_day = utility.get_entity_by_date(datastore_client, marketday.kind, requested_date)
    market_day = list(market_day)
    model_list = []

    if market_day:
        market_day = market_day[0]

        for active_model in model.active_model_list:
            entity = utility.get_entity_by_date(datastore_client, active_model.kind, requested_date)
            entity = list(entity)
            if entity:
                entity = entity[0]
                if entity[constants.DATE].date() != requested_date:
                    print(
                        "Requested date does not match entity for",
                        active_model.kind
                    )
                else:
                    first_entity = list(utility.get_first_entity(datastore_client, active_model.kind))[0]
                    balance_as_cash = (entity[constants.CASH_BALANCE] + utility.convert_btc_to_cash(
                            entity[constants.BTC_BALANCE],
                            market_day[constants.CLOSE_PRICE]
                        )
                    )
                    balance_as_btc = (entity[constants.BTC_BALANCE] + utility.convert_cash_to_btc(
                            entity[constants.CASH_BALANCE],
                            market_day[constants.CLOSE_PRICE]
                        )
                    )

                    list_days_holding_cash = entity[constants.LIST_CONSECUTIVE_DAYS_HOLDING_CASH] 
                    list_days_holding_cash.append(entity[constants.CONSECUTIVE_DAYS_HOLDING_CASH])
                    list_days_holding_btc = entity[constants.LIST_CONSECUTIVE_DAYS_HOLDING_BTC]
                    list_days_holding_btc.append(entity[constants.CONSECUTIVE_DAYS_HOLDING_BTC])
                    total_return = utility.get_rate_of_return(balance_as_cash, constants.HISTORICAL_STARTING_CASH_BALANCE)
                    duration = (market_day[constants.DATE] - first_entity[constants.DATE]).days + 1
                    duration_in_years = relativedelta(market_day[constants.DATE], first_entity[constants.DATE]).years
                    duration_of_months = relativedelta(market_day[constants.DATE], first_entity[constants.DATE]).months
                    days_holding_cash = sum(list_days_holding_cash) if list_days_holding_cash else 0
                    days_holding_btc = sum(list_days_holding_btc) if list_days_holding_btc else 0
                    avg_return_on_sells = utility.calculate_average_from_list(entity[constants.LIST_RETURNS_PER_SELL])
                    avg_return_on_buys = utility.calculate_average_from_list(entity[constants.LIST_RETURNS_PER_BUY])
                    prev_trans_price = entity[constants.PREVIOUS_TRANSACTION_CLOSE_PRICE]

                    if entity[constants.BTC_BALANCE] > 0:
                        price_target = 250000 if avg_return_on_sells == 0 else (avg_return_on_sells / 100) * prev_trans_price + prev_trans_price
                    else:
                        price_target = prev_trans_price / ((avg_return_on_buys / 100) + 1)

                    dictionary = {
                        'alias': active_model.alias,
                        'description': active_model.description,
                        'image_url': active_model.image_url,
                        'recommendation': entity[constants.RECOMMENDATION],
                        'net_profit': f'${balance_as_cash - constants.HISTORICAL_STARTING_CASH_BALANCE:,.0f}',
                        'total_return_float': total_return,
                        'total_return': f'{total_return:,.0f}%',
                        'duration': f'{duration_in_years:,.0f} {utility.pluralize("yr", duration_of_months)} {duration_of_months} {utility.pluralize("mo", duration_of_months)}',
                        'starting_balance': f'${constants.HISTORICAL_STARTING_CASH_BALANCE:,.2f}',
                        'balance_as_cash': f'${balance_as_cash:,.2f}',
                        'balance_as_btc': f'{balance_as_btc:,.1f} BTC',
                        'cash_balance': f'${entity[constants.CASH_BALANCE]:,.2f}',
                        'btc_balance': f'{entity[constants.BTC_BALANCE]:,.1f} BTC',
                        'days_holding_cash': days_holding_cash,
                        'percent_days_holding_cash': f'{0 if duration == 0 else days_holding_cash / duration * 100:,.0f}%',
                        'days_holding_btc': days_holding_btc,
                        'percent_days_holding_btc': f'{0 if duration == 0 else days_holding_btc / duration * 100:,.0f}%',
                        'avg_days_holding_cash': f'{ utility.calculate_average_from_list(list_days_holding_cash):,.0f}',
                        'avg_days_holding_btc': f'{ utility.calculate_average_from_list(list_days_holding_btc):,.0f}',
                        'avg_return_on_buys': f'{avg_return_on_buys:,.0f}%',
                        'avg_return_on_sells': f'{avg_return_on_sells:,.0f}%',
                        'number_of_transactions': len(entity[constants.LIST_RETURNS_PER_BUY]) + len(entity[constants.LIST_RETURNS_PER_SELL]),
                        'days_since_transaction': f'{max(entity[constants.CONSECUTIVE_DAYS_HOLDING_BTC], entity[constants.CONSECUTIVE_DAYS_HOLDING_CASH]):,.0f} days',
                        'next_transaction_type': 'Sell' if balance_as_btc > 0 else 'Buy',
                        'price_target': f'${price_target:,.0f}'
                    }
                    model_list.append(dictionary)

        # Populate the review stars
        list_returns = [a_dict['total_return_float'] for a_dict in model_list]
        list_returns.sort(reverse=True)
        star_count = 5
        for r in list_returns:
            for m in model_list:
                if m['total_return_float'] == r:
                    m['star_count'] = star_count
                    if star_count > 1:
                        star_count -= 1
    else:
        market_day = {}

    return {
        'date': utility.custom_strftime(requested_date),
        'next_date': requested_date + one_day,
        'previous_date': requested_date - one_day,
        'market_day': market_day,
        'models': model_list
    }
