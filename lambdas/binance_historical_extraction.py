# ./lambdas/binance_historical_extraction.py
from datetime import datetime
import json
#
from binance import TradeIDFinder

CHUNK_LIMIT = 1e3
DATEFORMAT = "%Y-%m-%d"
RESERVED_CONCURRENCY = 4
SQS_QUEUE_NAME_EXTRACTION = ''
SQS_QUEUE_NAME_DELAY_DAY = ''
SQS_QUEUE_NAME_DELAY_HOUR = ''
SQS_QUEUE_NAME_DELAY_MINUTE = ''
SQS_QUEUE_NAME_DELAY_SECOND = ''

def parse_date(date: str) -> datetime:

    return datetime.strptime(date, DATEFORMAT)


def parse_event(payload: dict):
    if (type_ := payload['type']) == 'orchestration':
        # user sent configuration
        handle_orchestration(payload['config'])
    elif type_ == 'api_call':
        # sqs sent the payload to send as GET to API
        handle_api_call(payload['config'])
    else:
        raise Exception("lambda only accepts api_call or orchestration")
    
    return


def ensure_sqs_trigger(record):
    if (event_source := record["eventSource"]) != "aws:sqs":
        raise Exception(f"Event source must be aws:sqs not {event_source = }")

    return


def handle_orchestration(config: dict):
    start_date: str = config.get('start_date')
    end_date: str = config.get('end_date')
    reverse: bool = config.get('reverse')
    symbol: str = config.get('symbol')

    if reverse:
        handle_reverse_load(symbol, start_date)
    else:
        if not start_date:
            handle_from_start(symbol, end_date)
        else:
            handle_from_date(symbol, start_date, end_date)

    return


def make_config(start_date: str = '', end_date: str = '', reverse: bool = False):
    config = dict()
    if start_date:
        config['start_date'] = start_date
    if end_date:
        config['end_date'] = end_date

    config['reverse'] = reverse

    return config


def create_payload(symbol: str, trade_id: int) -> dict:

    return {"symbol": symbol, "limit": CHUNK_LIMIT, "fromId": trade_id}


def send_sqs_message(queue_name: str, message: dict):
    message = json.dumps(message)

    # TO DO send the message to the SQS queue
    #
    #

    return


def handle_reverse_load(symbol: str, start_date: str = ''):
    latest_trade_id = get_latest_trade_id(symbol)

    config = make_config(start_date, reverse=True)

    starting_ids = get_starting_ids(latest_trade_id, RESERVED_CONCURRENCY, CHUNK_LIMIT, reverse=True)
    for id_ in starting_ids:
        payload = create_payload(symbol, id_)
        config['payload'] = payload

        message = {"config": config, "type": "api_call"}
        send_sqs_message(message)

    return


def handle_from_date(symbol: str, start_date: str, end_date: str = ''):
    start_date = parse_date(start_date)
    trade_id_finder = TradeIDFinder(symbol, start_date)
    trade_id = trade_id_finder.get_trade_id_for_date(start_date)

    config = make_config(start_date, end_date)

    starting_ids = get_starting_ids(trade_id, RESERVED_CONCURRENCY, CHUNK_LIMIT)
    for id_ in starting_ids:
        payload = create_payload(symbol, id_)
        config['payload'] = payload

        message = {"config": config, "type": "api_call"}
        send_sqs_message(SQS_QUEUE_NAME_EXTRACTION, message)

    return


def handle_from_start(symbol, end_date: str = ''):
    trade_id = 0 # assumed true

    config = make_config(end_date)

    starting_ids = get_starting_ids(trade_id, RESERVED_CONCURRENCY, CHUNK_LIMIT)
    for id_ in starting_ids:
        payload = create_payload(symbol, id_)
        config['payload'] = payload

        message = {"config": config, "type": "api_call"}
        send_sqs_message(message)

    return


def make_candidate_id(trade_id: int, delta: int, reverse: bool=False):
    if reverse:
        candidate_id = trade_id - delta
    else:
        candidate_id = trade_id + delta

    return candidate_id


def get_starting_ids(trade_id, concurrency, chunk_size, reverse=False):
    starting_ids = []
    for i in range(1, concurrency + 1):
        delta = i*chunk_size
        if (candidate_id := make_candidate_id(trade_id, delta, reverse)) >= 0:
                starting_ids.append(candidate_id)

    return starting_ids


def handle_api_call(config: dict):
    payload = config['payload']

    binance_query_api = BinanceQueryAPI()

    status_code, res = binance_query_api.old_trade_lookup(payload['symbol'], CHUNK_LIMIT, payload['fromId'])

    if status_code in [418, 429]:
        handle_rate_limit(status_code, res, config)

    # TO DO: store result to file
    #
    #

    else:
        delta = RESERVED_CONCURRENCY * CHUNK_LIMIT
        next_trade_id = make_candidate_id(payload['fromId'], delta, config['reverse'])

        if (len(res) == CHUNK_LIMIT) and (next_trade_id >= 0):
            config['payload']['fromId'] = next_trade_id
            message = {'config': config, 'type': 'api_call'}
            send_sqs_message(message)

    return


def handle_rate_limit(status_code: int, api_response: dict, config: dict):
    """
    when asked to wait x seconds before retrying API for throttling or ban, send to the delay queue
    which will feed a separate delay lambda. The delay lambda will decrement the penalties and refeed
    the delay queue until there are none left. When penalty time has expired, that delay lambda will 
    feed this lambda once again with the failed query config.
    """
    delay_config = get_delay_config(api_response)
    message = {"status_code": status_code, "delay_config": delay_config, "config": config}

    penalty_types = ['day', 'hour', 'minute', 'second']
    sqs_queue_names = map(lambda x: f'SQS_QUEUE_NAME_DELAY_{x.upper()}', penalty_types)
    penalties = map(lambda x: delay_config[x], penalty_types)

    for penalty, queue_name in zip(penalties, sqs_queue_names):
        if penalty:
            send_sqs_message(queue_name, message)
            break
    return


def get_delay_config(api_response: dict):
    # doing a bit of guessing around what this response looks like but enough to get the picture
    retry_seconds = api_response['retry_after']
    unix_datetime = datetime.fromtimestamp(retry_seconds)

    delay_config = {
                "day": unix_datetime.day - 1,
                "hour": unix_datetime.hour - 1,
                "minute": unix_datetime.minute - 1,
                "second": unix_datetime.second
            }

    return delay_config

def handle_record(record: dict):
    payload = json.loads(record['body'])
    parse_event(record)

    return

def handler(event, _):
    for record in event['Records']:
        ensure_sqs_trigger(record)
        handle_record(record)

    return {"status_code": 200}
