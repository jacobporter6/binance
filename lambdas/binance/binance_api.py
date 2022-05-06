# ./lambdas/binance/binance_api.py
import json
from urllib import request

BASE_ENDPOINT = 'https://api.binance.com'

def encode_params(parameters: dict) -> str:
    
    return request.parse.urlencode(parameters)

def url_builder(base, api_endpoint, parameters: dict):
    endcoded_parameters = encode_params(parameters)
    if not api_endpoint.startswith('/'):
        api_endpoint = '/' + api_endpoint

    return f"{base}{api_endpoint}?{encoded_parameters}"

def read_json(response) -> dict:
    response_body = response.read()
    
    return json.loads(response_body.decode("utf-8"))


class BinanceQueryAPI:
    def __init__(self):
        return

    def connectivity_test(self):
        api_endpoint = '/api/v3/ping'

        url = BASE_ENDPOINT + api_endpoint

        response = request.urlopen(url)

        return read_json(response)

    def old_trade_lookup(self, symbol, limit: int=500, from_id: int=0):
        api_endpoint = '/api/v3/historicalTrades'

        parameters = {"symbol": symbol, "limit": limit}
        if from_id:
            parameters["fromId"] = from_id

        url = url_builder(BASE_ENDPOINT, api_endpoint, parameters)

        response = request.urlopen(url)
