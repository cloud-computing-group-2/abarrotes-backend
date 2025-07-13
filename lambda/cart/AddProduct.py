import boto3 
import json
import os
from decimal import Decimal
import uuid
from datetime import datetime

stage = os.environ.get('stage')
table_cart = os.environ.get('TABLE_CART', 'dev-t-carrito')
print(f"Stage: {stage}")
user_validar = f"abarrotes-usuarios-{stage}-validar"
print(f"User validation function: {user_validar}")
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
    producto = dynamodb.Table(table_products)

    user_id = body["user_id"]
    product_id = body["product_id"]
    amount = body["amount"]

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

    # verificamos el stock del producto en la tabla producto

    if stock <= 0 or stock < amount:
        return cors_response(400, {
            'message': f"No hay suficiente stock para el producto. Stock disponible: {stock}, cantidad solicitada: {amount}"
        })

    new_stock = stock - amount

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
    
    # verificamos si el usuario ya tiene un carrito creado, si 
    # no lo tiene lo creamos

    response = carrito.get_item(
        Key={
            'tenant_id': tenant_id,  
            'user_id': user_id      
        }
    )

    new_price = Decimal(str(precio * amount))  # precio del prod * cantidad

    new_product = {
#            'tenant_id': tenant_id,
            'product_id': product_id, 
            'nombre': nombre,
            'amount': amount,          
            'price': new_price  # precio del prod * cantidad
        }
    # no verifica i el producto ya está en el carrito del usuario eso se hará en PUT
    if 'Item' in response: # existe

        print("Carrito encontrado, actualizando productos...")

        update_response = carrito.update_item(
            Key={
                'tenant_id': tenant_id,
                'user_id': user_id
            },
            UpdateExpression="SET products = list_append(products, :new_product)", 
            ExpressionAttributeValues={
                ':new_product': [new_product] 
            },
            ReturnValues="UPDATED_NEW" 
        )

        carrito.update_item(
            Key={
                'tenant_id': tenant_id,
                'user_id': user_id
            },
            UpdateExpression="SET total_price = total_price + :new_price", 
            ExpressionAttributeValues={
                ':new_price': new_price 
            },
            ReturnValues="UPDATED_NEW" 
        )

        print("Respuesta de la actualización:", update_response)

    else:
        print("Carrito no encontrado, creando nuevo carrito...")

        cart_id = str(uuid.uuid4())  
        created_at = datetime.now().isoformat()
        
        item = {
            'tenant_id': tenant_id,  
            'user_id': user_id,     
            'cart_id': cart_id,      
            'created_at': created_at,  
            'products': [new_product],  
            'total_price': new_price
        }

        response = carrito.put_item(Item=item)

        print("Respuesta de la creación del carrito:", response)

    return cors_response(200, {'message': 'Ítem insertado correctamente.'})



