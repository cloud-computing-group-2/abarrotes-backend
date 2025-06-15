import boto3 
import json
from boto3.dynamodb.conditions import Key 
from decimal import Decimal
from datetime import datetime

table_cart = "ab_carrito"
table_historial = "ab_historial"
user_validar = "abarrotes-usuarios-dev-validar"

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
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }


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
        carrito_item['completed_at'] = datetime.now().isoformat() 


        put_response = historial.put_item(
            Item=carrito_item  
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Carrito copiado con éxito a la tabla historial.',
                'response': put_response
            })
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Carrito no encontrado.'})
        }

