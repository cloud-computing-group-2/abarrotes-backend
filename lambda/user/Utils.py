import json

def load_body(event):
    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])
