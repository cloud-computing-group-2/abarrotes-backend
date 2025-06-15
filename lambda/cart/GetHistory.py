import boto3 
import json
import os
from datetime import datetime

stage = os.environ.get('stage')
table_historial = os.environ.get('TABLE_CART', 'dev-t-carrito')+"-history"
user_validar = f"abarrotes-usuarios-{stage}-validar"

def lambda_handler(event, context):

    print(event)
    # Entrada (json)
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
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

    params = {
        'Limit': limit
    }

    last_evaluated_key = query_params.get('last_evaluated_key')
    if last_evaluated_key:
        try:
            params['ExclusiveStartKey'] = json.loads(last_evaluated_key)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'last_evaluated_key no es válido'})
            }

    try:
        response = historial.scan(**params)

        items = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey', None)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'items': items,  # Elementos obtenidos
                'last_evaluated_key': last_evaluated_key  # Clave para la siguiente página de resultados
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error al acceder a DynamoDB: {str(e)}'})
        }