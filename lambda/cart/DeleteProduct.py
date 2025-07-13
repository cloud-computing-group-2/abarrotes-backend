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
            'Access-Control-Allow-Methods': 'OPTIONS,POST,PUT'
        },
        'body': json.dumps(body_dict)
    }

def lambda_handler(event, context):

    if event['httpMethod'] == 'OPTIONS':
        return cors_response(200, {'message': 'CORS preflight OK'})

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
    producto = dynamodb.Table(table_products)

    user_id = body["user_id"]
    product_id = body["product_id"]

    # encontrando la información del producto
    
    info_prod = producto.get_item(
        Key={
            'tenant_id': tenant_id,
            'producto_id': product_id 
        }
    )

    print("Información del producto:")
    print(info_prod)

    info = info_prod['Item']
    nombre = info['nombre']
    precio = info['precio']
    stock = info['stock']

    # encontrando el carrito del usuario

    response = carrito.get_item(
        Key={
            'tenant_id': tenant_id,  
            'user_id': user_id      
        }
    )

    # buscando el producto en el carrito

    products = response['Item']['products']
    curr_amount = 0
    curr_total_price = response['Item']['total_price']

    # Buscar el producto en la lista de productos
    product_found = False
    for product in products:
        if product['product_id'] == product_id:
            curr_amount = product['amount']
            products.remove(product)  
            product_found = True
            break

    new_price = curr_total_price - (curr_amount * precio)
    new_stock = stock + curr_amount

    
    if product_found:
        update_response = carrito.update_item(
            Key={
                'tenant_id': tenant_id,
                'user_id': user_id
            },
            UpdateExpression="SET products = :new_products",  # se actualiza toda la lista de productos
            ExpressionAttributeValues={
                ':new_products': products 
            },
            ReturnValues="UPDATED_NEW"  
        )

        update_response = carrito.update_item(
            Key={
                'tenant_id': tenant_id,
                'user_id': user_id
            },
            UpdateExpression="SET total_price = :new_price",  # se actualiza precio total del carrito
            ExpressionAttributeValues={
                ':new_price': new_price
            },
            ReturnValues="UPDATED_NEW"  
        )
        print("Respuesta de la actualización:", update_response)
    else:
        print(f"Producto con ID {product_id} no encontrado en el carrito.")


    update_response = producto.update_item(
        Key={
            'tenant_id': tenant_id,  
            'producto_id': product_id  
        },
        UpdateExpression="SET stock = :new_stock",  
        ExpressionAttributeValues={
            ':new_stock': Decimal(str(new_stock)) 
        },
        ReturnValues="UPDATED_NEW" 
        )
    
    
    return cors_response(200, {
        'message': 'Ítem actualizado correctamente.',
        'response': response 
    })


