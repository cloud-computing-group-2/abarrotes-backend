import boto3 
import json
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
        'body': json.dumps(body_dict, default=str)
    }

def consolidar_productos(productos):
    productos_dict = {}
    for p in productos:
        pid = p['product_id']
        if pid in productos_dict:
            productos_dict[pid]['amount'] += p['amount']
            productos_dict[pid]['price'] += p['price']
        else:
            productos_dict[pid] = dict(p)
    return list(productos_dict.values())

def lambda_handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return cors_response(200, {'message': 'CORS preflight OK'})

    body = json.loads(event['body'])
    token = event['headers']['Authorization']
    tenant_id = body['tenant_id']
    user_id = body['user_id']
    product_id = body['product_id']
    amount = body['amount']

    # Validar token
    lambda_client = boto3.client('lambda')    
    payload = {
        "token": token,
        "tenant_id": tenant_id
    }
    invoke_response = lambda_client.invoke(
        FunctionName=user_validar,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    response = json.loads(invoke_response['Payload'].read())
    if response['statusCode'] == 403:
        return cors_response(403, {'message': 'Forbidden - Acceso No Autorizado'})

    # Acceso a las tablas
    dynamodb = boto3.resource('dynamodb')
    carrito = dynamodb.Table(table_cart)
    producto = dynamodb.Table(table_products)

    # Obtener producto
    info_prod = producto.get_item(
        Key={
            'tenant_id': tenant_id,
            'producto_id': product_id 
        }
    )

    if 'Item' not in info_prod:
        return cors_response(404, {'message': 'Producto no encontrado.'})

    info = info_prod['Item']
    nombre = info['nombre']
    precio = info['precio']
    stock = info['stock']

    # Obtener carrito
    response = carrito.get_item(
        Key={
            'tenant_id': tenant_id,  
            'user_id': user_id      
        }
    )

    if 'Item' not in response:
        return cors_response(404, {'message': 'Carrito no encontrado.'})

    products = response['Item']['products']
    curr_total_price = response['Item']['total_price']

    # Consolidar duplicados
    products = consolidar_productos(products)

    # Buscar el producto y actualizar cantidad
    product_found = False
    new_stock = stock
    for product in products:
        if product['product_id'] == product_id:
            curr_amount = product['amount']
            if curr_amount >= amount:
                product['amount'] = amount
                product['price'] = Decimal(precio * amount)
                new_stock = stock + (curr_amount - amount)
            else:
                if amount - curr_amount <= stock:
                    product['amount'] = amount
                    product['price'] = Decimal(precio * amount)
                    new_stock = stock - (amount - curr_amount)
                else:
                    return cors_response(400, {
                        'message': f"No hay suficiente stock para el producto. Stock disponible: {stock}, cantidad solicitada: {amount}"
                    })
            product_found = True
            break

    if not product_found:
        return cors_response(404, {'message': 'Producto no está en el carrito.'})

    # Recalcular el precio total
    new_price = curr_total_price - (curr_amount * precio) + (amount * precio)

    # Actualizar carrito
    carrito.update_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        },
        UpdateExpression="SET products = :new_products, total_price = :new_price",
        ExpressionAttributeValues={
            ':new_products': products,
            ':new_price': Decimal(new_price)
        },
        ReturnValues="UPDATED_NEW"
    )

    # Actualizar stock del producto
    producto.update_item(
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

    return cors_response(200, {'message': 'Ítem actualizado correctamente.'})
