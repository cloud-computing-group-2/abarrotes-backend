import boto3
import hashlib
import bcrypt
import uuid  # Genera valores únicos
from Utils import load_body
from datetime import datetime, timedelta

# Expire time
expire_time = timedelta(hours=5)

table_users = "ab_usuarios"
table_tokens = "ab_tokens_acceso"

# Hashear contraseña
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())



def lambda_handler(event, context):
    body = load_body(event)

    user_id = body.get('user_id')
    tenant_id = body.get('tenant_id')
    password = body.get('password')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_users)
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Usuario no existe'
        }
    else:
        hashed_password_bd = response['Item']['password']
        if verify_password(password, hashed_password_bd):
            # Genera token
            token = str(uuid.uuid4())
            fecha_hora_exp = datetime.now() + expire_time
            item_token = {
                'token': token,
                'user_id': user_id,
                "tenant_id": tenant_id,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
            }
            table = dynamodb.Table(table_tokens)
            dynamodbResponse = table.put_item(Item=item_token)
        else:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }


    return {
        'statusCode': 200,
        'token': token
    }