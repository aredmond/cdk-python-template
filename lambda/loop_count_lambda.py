import json

def handler(event, context):
    ### Simple pass through AWS Lambda function
    print(f'request: {json.dumps(event)}')

    if 'loop_count' in event:
        if event['loop_count'] >= 3:
            event['status'] = 'SUCCEEDED'
        else:
            event['loop_count'] += 1
    else:
        event['loop_count'] = 1
        event['status'] = 'PROCESSING'
    # return {
    #     'statusCode': 200,
    #     'headers': {
    #         'Content-Type': 'text/plain'
    #     },
    #     'body': 'This is a pass through lambda for a stepfunction.'
    # }
    return event