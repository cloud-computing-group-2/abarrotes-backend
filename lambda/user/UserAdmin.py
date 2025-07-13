import boto3
from datetime import datetime
import json
import os

def load_body(event):
    if 'body' not in event:
        return event
    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])

def lambda_handler(event, context):
    print('Event:', event)

    body = load_body(event)
    token = body.get('token')
    tenant_id = body.get('tenant_id')

    if not token or not tenant_id:
        return {
            'statusCode': 403,
            'body': json.dumps('Missing token or tenant_id')
        }

    dynamodb = boto3.resource('dynamodb')
    table_auth = dynamodb.Table(os.environ['TABLE_AUTH'])
    table_user = dynamodb.Table(os.environ['TABLE_USER'])

    # Buscar token en tabla de autenticación
    auth_response = table_auth.get_item(
        Key={
            'token': token,
            'tenant_id': tenant_id
        }
    )
    print("Auth response:", auth_response)

    if 'Item' not in auth_response:
        return {
            'statusCode': 403,
            'body': json.dumps('Token no existe')
        }

    item = auth_response['Item']
    user_id = item.get('user_id')
    expires = item.get('expires_at')

    # Validar tenant
    if item.get('tenant_id') != tenant_id:
        return {
            'statusCode': 403,
            'body': json.dumps('Token no corresponde al tenant')
        }

    # Validar expiración
    now = datetime.now().isoformat()
    if now > expires:
        return {
            'statusCode': 403,
            'body': json.dumps('Token expirado')
        }

    # Obtener usuario
    user_response = table_user.get_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        }
    )
    print("User response:", user_response)

    if 'Item' not in user_response:
        return {
            'statusCode': 403,
            'body': json.dumps('Usuario no encontrado')
        }

    rol = user_response['Item'].get('rol')
    if rol != 'ADMIN':
        return {
            'statusCode': 403,
            'body': json.dumps('Acceso restringido a administradores')
        }

    # Validación exitosa
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Token válido y usuario administrador',
            'user_id': user_id,
            'rol': rol
        })
    }
