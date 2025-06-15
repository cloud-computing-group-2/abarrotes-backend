import boto3 
import json
from boto3.dynamodb.conditions import Key 
from decimal import Decimal
import uuid
from datetime import datetime

table_cart = "ab_carrito"
table_products = "ab_productos"
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
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"No hay suficiente stock para el producto. Stock disponible: {stock}, cantidad solicitada: {amount}"
            })
        }

    new_stock = stock - amount

    update_response = producto.update_item(
        Key={
            'tenant_id': tenant_id,  
            'product_id': product_id  
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

    new_product = {
#            'tenant_id': tenant_id,
            'product_id': product_id, 
            'nombre': nombre,
            'amount': amount,          
            'precio': Decimal(str(precio * amount))  # precio del prod * cantidad
        }

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
            'total_price': new_product['price']
        }

        response = carrito.put_item(Item=item)

        print("Respuesta de la creación del carrito:", response)

    return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Ítem insertado correctamente.',
#                'response': response  
            })
        }

