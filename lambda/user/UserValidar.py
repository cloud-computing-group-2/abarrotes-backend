import boto3
from Utils import load_body
from datetime import datetime

def lambda_handler(event, context):

    print(event)

    body = load_body(event)

    token = body.get('token')
    tenant_id = body.get('tenant_id')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ab_tokens_acceso')
    response = table.get_item(
        Key={
            'token': token,
            "tenant_id": tenant_id
        }
    )
    if 'Item' not in response or response['Item'].get('tenant_id') != tenant_id:
        print("error with ", tenant_id, " response: ", response)
        return {
            'statusCode': 403,
            'body': 'Token no existe'
        }
    else:
        expires = response['Item']['expires']
        print("expires ", expires)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if now > expires:
            return {
                'statusCode': 403,
                'body': 'Token expirado'
            }

    print("success")
    return {
        'statusCode': 200,
        'body': 'Token válido'
    }