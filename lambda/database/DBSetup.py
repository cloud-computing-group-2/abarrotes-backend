import boto3
import json
import os

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb')
    stage = os.environ.get("STAGE", "dev")

    # Tabla prefijada por stage
    def stage_table(name):
        return f"{stage}_{name}"

    try:
        # Lista de tablas
        tables = {
            'ab_usuarios': {
                'AttributeDefinitions': [
                    {'AttributeName': 'tenant_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                'KeySchema': [
                    {'AttributeName': 'tenant_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
                ]
            },
            'ab_tokens_acceso': {
                'AttributeDefinitions': [
                    {'AttributeName': 'token', 'AttributeType': 'S'},
                    {'AttributeName': 'tenant_id', 'AttributeType': 'S'}
                ],
                'KeySchema': [
                    {'AttributeName': 'token', 'KeyType': 'HASH'},
                    {'AttributeName': 'tenant_id', 'KeyType': 'RANGE'}
                ]
            },
            'ab_productos': {
                'AttributeDefinitions': [
                    {'AttributeName': 'tenant_id', 'AttributeType': 'S'},
                    {'AttributeName': 'producto_id', 'AttributeType': 'S'}
                ],
                'KeySchema': [
                    {'AttributeName': 'tenant_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'producto_id', 'KeyType': 'RANGE'}
                ]
            },
            'ab_carrito': {
                'AttributeDefinitions': [
                    {'AttributeName': 'tenant_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                'KeySchema': [
                    {'AttributeName': 'tenant_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
                ]
            },
            'ab_historial': {
                'AttributeDefinitions': [
                    {'AttributeName': 'tenant_id', 'AttributeType': 'S'},
                    {'AttributeName': 'compra_id', 'AttributeType': 'S'}
                ],
                'KeySchema': [
                    {'AttributeName': 'tenant_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'compra_id', 'KeyType': 'RANGE'}
                ]
            }
        }

        created = []

        for name, config in tables.items():
            table_name = stage_table(name)
            try:
                dynamodb.create_table(
                    TableName=table_name,
                    AttributeDefinitions=config['AttributeDefinitions'],
                    KeySchema=config['KeySchema'],
                    BillingMode='PAY_PER_REQUEST',
                    Tags=[{'Key': 'Environment', 'Value': stage}]
                )
                created.append(table_name)
            except dynamodb.exceptions.ResourceInUseException:
                pass  # ya existe

        return {
            'statusCode': 200,
            'body': json.dumps(f'Tablas creadas o ya existentes: {created}')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
