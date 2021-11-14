#!/usr/bin/env python3

import json
import datetime

import urllib3

from scrape_cot_gov import cot_status
ESKOM_API_URL = "https://loadshedding.eskom.co.za/LoadShedding/GetStatus"


def eskom_status():
    http = urllib3.PoolManager()
    resp = http.request("GET", ESKOM_API_URL)

    return int(resp.data.decode()) - 1


stage_cache = dict()


def refresh_cache(api, timeout):
    n = datetime.datetime.now()

    if api not in stage_cache:
        stage_cache[api] = {
            'stage': None,
            'time': datetime.datetime.min
        }

    if ((n - stage_cache[api]['time']) > timeout):
        stage_cache[api]['stage'] = api()
        stage_cache[api]['time'] = datetime.datetime.now()

    return {
        'stage': stage_cache[api]['stage'],
        'time': stage_cache[api]['time'].isoformat()
    } 


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """


    timeout = datetime.timedelta(minutes=2) 
    apis = [eskom_status, cot_status]
    apis = {api.__name__: refresh_cache(api, timeout) for api in apis}
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": apis,
        }),
    }


if __name__ == "__main__":
    # event and context are currently unused
    lambda_ret = lambda_handler(event=None, context=None)
    # normalize JSON
    lambda_ret['body'] = json.loads(lambda_ret['body'])

    print(json.dumps(lambda_ret))
