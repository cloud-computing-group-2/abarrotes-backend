import json

import json

def load_body(event):
    if 'body' not in event:
        return event
    
    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])


