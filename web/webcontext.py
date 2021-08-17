from utilities import utility, constants
from jobs import marketday
import datetime
from models import model


one_day = datetime.timedelta(days = 1)

def build_bot_summary_context_by_day(datastore_client, requested_date):
    market_day = utility.get_entity_by_date(datastore_client, marketday.kind, requested_date)

    market_day = list(market_day)

    if market_day:
        market_day = market_day[0]
        model_list = []
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
                    dictionary = {
                        'alias': active_model.alias,
                        'image_url': active_model.image_url,
                        'recommendation': entity[constants.RECOMMENDATION],
                        'net_profit': f'${entity[constants.NET_PROFIT_IN_CASH]:,.2f}',
                        'total_return': f'{entity[constants.TOTAL_RETURN]:,.0f}%',
                        'duration': f'{(market_day[constants.DATE] - first_entity[constants.DATE]).days:,.0f} days',
                        'starting_balance': f'${constants.HISTORICAL_STARTING_CASH_BALANCE:,.2f}',
                        'balance_as_cash': f'${balance_as_cash:,.2f}',
                        'balance_as_btc': f'{balance_as_btc:,.1f} BTC',
                        'cash_balance': f'${entity[constants.CASH_BALANCE]:,.2f}',
                        'btc_balance': f'{entity[constants.BTC_BALANCE]:,.1f} BTC',
                        'days_holding_cash': entity[constants.TOTAL_DAYS_HOLDING_CASH] + entity[constants.CONSECUTIVE_DAYS_HOLDING_CASH],
                        'days_holding_btc': entity[constants.TOTAL_DAYS_HOLDING_BTC] + entity[constants.CONSECUTIVE_DAYS_HOLDING_BTC],
                        'avg_days_holding_cash': f'{entity[constants.AVG_DAYS_HOLDING_CASH]:,.1f}',
                        'avg_days_holding_btc': f'{entity[constants.AVG_DAYS_HOLDING_BTC]:,.1f}',
                        'avg_return_on_buys': f'{entity[constants.AVG_RETURN_ON_BUYS]:,.0f}%',
                        'avg_return_on_sells': f'{entity[constants.AVG_RETURN_ON_SELLS]:,.0f}%',
                        'days_since_transaction': f'{max(entity[constants.CONSECUTIVE_DAYS_HOLDING_BTC], entity[constants.CONSECUTIVE_DAYS_HOLDING_CASH]):,.0f} days'
                    }
                    model_list.append(dictionary)

    else:
        market_day = {}

    return {
        'date': utility.custom_strftime(requested_date),
        'next_date': requested_date + one_day,
        'previous_date': requested_date - one_day,
        'market_day': market_day,
        'models': model_list
    }

