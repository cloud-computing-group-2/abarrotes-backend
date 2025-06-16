import boto3 
import json
import os
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key

stage = os.environ.get('stage')
table_historial = os.environ.get('TABLE_CART', 'dev-t-carrito')+"-history"
user_validar = f"abarrotes-usuarios-{stage}-validar"

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    else:
        return obj

def lambda_handler(event, context):

    print(event)
    # Entrada (json)
    query_params = event.get('queryStringParameters', {})
    tenant_id = query_params.get('tenant_id')
    limit = int(query_params.get('limit', 10))
    
    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']

    lambda_client = boto3.client('lambda')    
    payload = {
    "token": token,
    "tenant_id": tenant_id
    }
    invoke_response = lambda_client.invoke(FunctionName=user_validar,
                                           InvocationType='RequestResponse',
                                           Payload = json.dumps(payload))
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    if response['statusCode'] == 403:
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }

    # Acceso a la BD
    dynamodb = boto3.resource('dynamodb')
    historial = dynamodb.Table(table_historial)

    # encontrando el historial del usuario

    params ={
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id),
            'Limit': limit
            }


    lek = query_params.get('last_evaluated_key')
    if lek:
        try:
            params['ExclusiveStartKey'] = json.loads(lek)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'last_evaluated_key no es válido'})
            }

    try:
        resp = historial.query(**params)
        items = decimal_to_float(resp.get('Items', []))
        next_key = resp.get('LastEvaluatedKey')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'items': items,
                'last_evaluated_key': json.dumps(next_key) if next_key else None
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error al consultar historial: {str(e)}'})
        }