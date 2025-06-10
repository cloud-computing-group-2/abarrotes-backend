import boto3
import json

table_name = 'ab_users'

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.create_table(
            TableName=table_name,
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
            BillingMode='PAY_PER_REQUEST',  # O usa ProvisionedThroughput si prefieres
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Dev'
                }
            ]
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f'Tabla {table_name} creada exitosamente.')
        }

    except dynamodb.exceptions.ResourceInUseException:
        return {
            'statusCode': 409,
            'body': json.dumps(f'La tabla {table_name} ya existe.')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
