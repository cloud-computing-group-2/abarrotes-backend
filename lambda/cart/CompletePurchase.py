import boto3 
import json
import os
from datetime import datetime

stage = os.environ.get('stage')
table_cart = os.environ.get('TABLE_CART', 'dev-t-carrito')
table_historial = os.environ.get('TABLE_CART', 'dev-t-carrito')+"-history"
user_validar = f"abarrotes-usuarios-{stage}-validar"
table_products = "ab_productos"

def cors_response(status_code, body_dict):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,PUT'
        },
        'body': json.dumps(body_dict)
    }


def lambda_handler(event, context):

    print(event)
    # Entrada (json)
    body =  json.loads(event['body'])
    
    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    tenant_id = body['tenant_id']

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
        return cors_response(403, {'message': 'Forbidden - Acceso No Autorizado'})

    # Acceso a la BD
    dynamodb = boto3.resource('dynamodb')
    carrito = dynamodb.Table(table_cart)
    historial = dynamodb.Table(table_historial)

    user_id = body["user_id"]

    # encontrando el carrito del usuario

    response = carrito.get_item(
        Key={
            'tenant_id': tenant_id,  
            'user_id': user_id     
        }
    )

    if 'Item' in response: 

        carrito_item = response['Item']
        carrito_item['tenant_id'] = f"{tenant_id}#{user_id}"
        carrito_item.pop('user_id', None)
        carrito_item['completed_at'] = datetime.now().isoformat() 

        put_response = historial.put_item(
            Item=carrito_item  
        )

        delete_response = carrito.delete_item(
            Key={
                'tenant_id': tenant_id,  
                'user_id': user_id
            }
        )

        return cors_response(200, {
            'message': 'Carrito copiado con éxito a la tabla historial.',
            'response': put_response
        })

    else:
        return cors_response(404, {'message': 'Carrito no encontrado.'})

