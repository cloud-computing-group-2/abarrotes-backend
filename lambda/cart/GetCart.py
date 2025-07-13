import boto3 
import json
from boto3.dynamodb.conditions import Key 
from decimal import Decimal
import os

stage = os.environ.get('stage')
table_cart = os.environ.get('TABLE_CART', 'dev-t-carrito')
user_validar = f"abarrotes-usuarios-{stage}-validar"
table_products = f"{stage}_ab_productos"


def cors_response(status_code, body_dict):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT,DELETE'
        },
        'body': json.dumps(body_dict)
    }

def lambda_handler(event, context):

    if event['httpMethod'] == 'OPTIONS':
        return cors_response(200, {'message': 'CORS preflight OK'})

    print(event)
    # Entrada (json)
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    tenant_id = query_params.get('tenant_id')

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
        return cors_response(403, {'message': 'Forbidden - Acceso No Autorizado'})

    # Acceso a la BD
    dynamodb = boto3.resource('dynamodb')
    carrito = dynamodb.Table(table_cart)

    # encontrando el carrito del usuario

    response = carrito.get_item(
        Key={
            'tenant_id': tenant_id,  
            'user_id': user_id      
        }
    )

    # buscando el producto en el carrito

    products = response['Item'].get('products', [])
    total_price = response['Item'].get('total_price', Decimal('0.0'))

    def decimal_to_float_or_str(obj):
        if isinstance(obj, Decimal):
            return float(obj) 
        elif isinstance(obj, list):
            return [decimal_to_float_or_str(item) for item in obj] 
        elif isinstance(obj, dict):
            return {key: decimal_to_float_or_str(value) for key, value in obj.items()}  
        return obj  
    products = decimal_to_float_or_str(products)
    
    return cors_response(200, {
        'message': 'Carrito encontrado.',
        'products': products, 
        'total_price': str(total_price)
    })


