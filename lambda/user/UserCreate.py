import boto3
import bcrypt
import json

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def load_body(event):
    if isinstance(event["body"], dict):
        return json.loads(event['body'])
    else:
        return event["body"]

# Función que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        print("raw event:", event)

        body = load_body(event)
        print("parsed body:", body)
        
        user_id = body.get('user_id')
        tenant_id = body.get('tenant_id')
        if not user_id or not tenant_id:
            return {
                "statusCode": 400,
                "body": "user_id or tenant_id invalid"
            }

        dynamodb = boto3.resource('dynamodb')
        ab_usuarios = dynamodb.Table('ab_usuarios')

        check = ab_usuarios.get_item(
            Key={
                'tenant_id': tenant_id,
                'user_id': user_id
            }
        )

        if "Item" in check:
            mensaje = {
                'error': 'User ya existe!'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

        password = body.get('password')

        # Verificar que el email y el password existen
        if user_id and password and tenant_id:
            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)
            # Conectar DynamoDB
            # Almacena los datos del user en la tabla de usuarios en DynamoDB
            ab_usuarios.put_item(
                Item={
                    'user_id': user_id,
                    'password': hashed_password,
                    "tenant_id": tenant_id,
                }
            )
            # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': 'User registered successfully',
                'user_id': user_id
            }
            return {
                'statusCode': 200,
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing user_id or password or tenant_id'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", e)
        mensaje = {
            'error': str(e)
        }
        return {
            'statusCode': 500,
            'body': mensaje
        }