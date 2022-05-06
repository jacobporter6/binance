# ./lambdas/binance_historical_extraction.py
import json
#
from binance import TradeIDFinder

def parse_event(payload: dict):
    type_ = payload['type']
    if type_ = 'orchestration':
        # user sent configuration
        handle_orchestration(payload['config'])
    elif type_ = 'api_call':
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

    return

def handle_api_call(config: dict):

    return

def handle_record(record: dict):
    payload = json.loads(record['body'])
    event_configuration = parse_event(record)

    return

def handler(event, _):
    for record in event['Records']:
        ensure_sqs_trigger(record)
        handle_record(record)

    return {"status_code": 200}
