# ./lambdas/binance/binance_utils.py
from datetime import datetime, timedelta
import itertools
import typing
#
from binance.binance_api import BinanceQueryAPI

def get_date(payload: dict):
    time_ms = payload['time']
    time_s = time_ms*1e-3

    return datetime.fromtimestamp(time_s)


def get_trade_id(payload: dict):

    return payload['id']


class TradeIDFinder:
    def __init__(self, symbol, start_date: typing.Optional[datetime]=None):
        self.symbol = symbol
        if start_date:
            self.start_date = start_date - timedelta(days=1)
        else:
            self.start_date = None
        self.query_api = BinanceQueryAPI()

        return

    def make_bounds(self, first_trade_payload: dict, last_trade_payload: dict):
        bounds = dict()
        for payload in [first_trade_payload, last_trade_payload]:
            bounds[get_trade_id(payload)] = get_date(payload)

        return bounds

    def estimate_trade_id(self, bounds: dict):
        fraction = self.get_fraction_from_days(self, **bounds.keys())

        return self.estimate_id(first_id, last_id, fraction)

    def get_fraction_from_days(self, first_date, last_date):
        days_before = (self.start_date - first_date).days
        total_days = (last_date - first_date).days

        return days_before/total_days

    def estimate_id(self, first_id, last_id, fraction):

        return round(first_id + ((last_id - first_id)*fraction))

    def retrieve_trade_id(self, trade_id) -> dict:
        status_code, trade_id_resp = self.query_api.old_trade_lookup(self.symbol, limit=1, from_id=trade_id)

        if status_code in [418, 429]:
            raise Exception("Cannot run pipeline right now as limit on API reached")

        return trade_id_resp

    def get_trade_id_for_date(self, bounds: dict) -> dict:
        estimated_id = self.estimate_id(bounds)
        estimated_id_payload = self.retrieve_trade_id(estimated_id)
        
        lower_id, upper_id = bounds.keys()
        
        estimated_id_date = get_date(estimated_id_payload)
        if estimated_id_date > self.start_date:
            new_bounds = {lower_id: bounds['lower_id'], estimated_id: estimated_id_date}
            return self.get_trade_id_for_date(new_bounds)

        elif estimated_id_date < self.start_date:
            new_bounds = {estimated_id: estimated_id_date, upper_id: bounds['upper_id']}
            return self.get_trade_id_for_date(new_bounds) 

        return estimated_id
