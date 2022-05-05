# ./lambdas/binance/binance_utils.py
from datetime import datetime
import itertools

def get_date(payload: dict):
    time_ms = payload['time']
    time_s = time_ms*1e-3

    return datetime.fromtimestamp(time_s)


def get_trade_id(payload: dict):

    return payload['id']


class TradeIDFinder:
    def __init__(self, start_date: datetime):
        self.start_date = start_date

        return

    def estimate_trade_id(self, first_trade_payload: dict, last_trade_payload: dict):
        first_date, first_id = get_date(first_trade_payload), get_trade_id(first_trade_payload)
        last_date, last_id = get_date(last_trade_payload), get_trade_id(last_trade_payload)

        fraction = self.get_fraction_from_days(self, first_date, last_date)

        return self.estimate_id(first_id, last_id, fraction)

    def get_fraction_from_days(self, first_date, last_date):
        days_before = (self.start_date - first_date).days
        total_days = (last_date - first_date).days

        return days_before/total_days

    def estimate_id(self, first_id, last_id, fraction):

        return round(first_id + ((last_id - first_id)*fraction))

