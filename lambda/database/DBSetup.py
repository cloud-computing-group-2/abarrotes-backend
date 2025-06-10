import boto3
import json

users = 'ab_usuarios'
tokens = 'ab_tokens_acceso'
products = "ab_productos"
shopping = "ab_compras"

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.create_table(
            TableName=users,
            AttributeDefinitions=[
                # Composite key: tenant_id + user_id
                {
                    'AttributeName': 'tenant_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'tenant_id',
                    'KeyType': 'HASH'  # Partition Key
                },
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'RANGE'  # Sort Key
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Dev'
                }
            ]
        )
        dynamodb.create_table(
            TableName=products,
            AttributeDefinitions=[
                {
                    'AttributeName': 'producto_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'tenant_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'tenant_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'producto_id',
                    'KeyType': 'RANGE'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Dev'
                }
            ]
        )
        dynamodb.create_table(
            TableName=shopping,
            AttributeDefinitions=[
                {
                    'AttributeName': 'compra_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'tenant_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'tenant_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'compra_id',
                    'KeyType': 'RANGE'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Dev'
                }
            ]
        )
        dynamodb.create_table(
            TableName=tokens,
            AttributeDefinitions=[
                {
                    'AttributeName': 'token',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'tenant_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'token',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'tenant_id',
                    'KeyType': 'RANGE'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Dev'
                }
            ]
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f'Tablas creadas exitosamente.')
        }

    except dynamodb.exceptions.ResourceInUseException:
        return {
            'statusCode': 409,
            'body': json.dumps(f'Las tablas ya existen.')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
