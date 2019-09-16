import json

def handler(event, context):
    ### Simple pass through AWS Lambda function
    print(f'request: {json.dumps(event)}')
    # return {
    #     'statusCode': 200,
    #     'headers': {
    #         'Content-Type': 'text/plain'
    #     },
    #     'body': 'This is a pass through lambda for a stepfunction.'
    # }
    return event