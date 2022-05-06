# ./lambdas/tests/test_binance_historical_extraction.py
import unittest
#
from binance_historical_extraction import *
from tests.fixtures import *

class TestBinanceHistoricalExtraction(unittest.TestCase):
    @unittest.expectedFailure
    def test_handler(self):
        self.assertTrue(0)
        return

    def test_make_config(self):
        with self.subTest("Reverse load, optional start_date"):
            self.assertEqual(configuration_1, make_config(start_date="2020-01-01", reverse=True))

        with self.subTest("Reverse load"):
            self.assertEqual(configuration_2, make_config(reverse=True))

        with self.subTest("load from trade_id=0, optional end_date"):
            self.assertEqual(configuration_3, make_config(end_date="2020-01-01"))

        with self.subTest("load from trade_id=0"):
            self.assertEqual(configuration_4, make_config())

        with self.subTest("load from date, optional end_date"):
            self.assertEqual(configuration_5, make_config(start_date="2020-01-01", end_date="2021-02-01"))

        with self.subTest("load from date"):
            self.assertEqual(configuration_6, make_config(start_date="2020-01-01"))

        return
