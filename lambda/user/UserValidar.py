import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Entrada (json)
    token = event['token']
    tenant_id = event['tenant_id']
    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_tokens_acceso')
    response = table.get_item(
        Key={
            'token': token
        }
    )
    if 'Item' not in response or response['Item'].get('tenant_id') != tenant_id:
        return {
            'statusCode': 403,
            'body': 'Token no existe'
        }
    else:
        expires = response['Item']['expires']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if now > expires:
            return {
                'statusCode': 403,
                'body': 'Token expirado'
            }

    # Salida (json)
    return {
        'statusCode': 200,
        'body': 'Token válido'
    }