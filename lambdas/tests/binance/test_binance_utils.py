# ./tests/binance/test_binance_utils.py
from datetime import datetime
import unittest
#
from binance.binance_utils import get_date
from binance.binance_utils import TradeIDFinder

class TestTradeIDFinder(unittest.TestCase):
    trade_id_finder = TradeIDFinder(datetime.now())
    payload = {
        "id": 28457,
        "price": "4.00000100",
        "qty": "12.00000000",
        "quoteQty": "48.000012",
        "time": 1499865549590,
        "isBuyerMaker": True,
        "isBestMatch": True
      }

    def test_get_date(self):
        date = get_date(self.payload)

        self.assertEqual(date, datetime(2017, 7, 12, 14, 19, 9, 590000))
        return

    def test_something(self):
        with self.subTest():
            first_id = 15
            last_id = 35
            fraction = 0.8

            estimate = self.trade_id_finder.estimate_id(first_id, last_id, fraction)
            self.assertEqual(estimate, 31)

        with self.subTest():
            first_id = 15
            last_id = 36
            fraction = 0.8

            estimate = self.trade_id_finder.estimate_id(first_id, last_id, fraction)
            self.assertEqual(estimate, 31)
        return
