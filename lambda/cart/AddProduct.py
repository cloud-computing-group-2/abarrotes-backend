import boto3 
import json
from boto3.dynamodb.conditions import Key 

table_name = "ab_carrito"

def lambda_handler(event, context):

    print(event)
    # Entrada (json)
    body =  event['body']
    
    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    tenant_id = body['tenant_id']

    lambda_client = boto3.client('lambda')    
    payload_string =  json.dumps({
        "token": token,
        "tenant_id": tenant_id 
    })
    invoke_response = lambda_client.invoke(FunctionName="UserValidar",
                                           InvocationType='RequestResponse',
                                           Payload = payload_string)
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    if response['statusCode'] == 403:
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }


    # Acceso a la BD
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.put_item(Item=body)

    return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Ítem insertado correctamente.',
                'response': response  
            })
        }

