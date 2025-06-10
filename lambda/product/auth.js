import AWS from 'aws-sdk';
const dynamo = new AWS.DynamoDB.DocumentClient();

export async function validateToken(token, tenant_id) {
  const res = await dynamo.get({
    TableName: 'ab_tokens_acceso',
    Key: { token, tenant_id }
  }).promise();

  if (!res.Item || new Date(res.Item.expires) < new Date()) {
    throw new Error('Token inválido o expirado');
  }
}