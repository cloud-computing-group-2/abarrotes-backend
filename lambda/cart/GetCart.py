import boto3 
import json
from boto3.dynamodb.conditions import Key 
from decimal import Decimal

table_cart = "ab_carrito"
table_products = "ab_productos"
user_validar = "abarrotes-usuarios-dev-validar"

def lambda_handler(event, context):

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
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }


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
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Carrito encontrado.',
            'products': products, 
            'total_price': str(total_price) 
        })
    }

