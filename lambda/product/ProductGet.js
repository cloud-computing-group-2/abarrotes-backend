const AWS = require('aws-sdk');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = 'ab_productos';

exports.handler = async (event) => {
  try {
    body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body
    const { token, producto_id, tenant_id } = body;
    await validateToken(token, tenant_id);

    const params = {
      TableName: tableName,
      KeyConditionExpression: 'tenant_id = :tid AND producto_id = :pid',
      ExpressionAttributeValues: {
        ':tid': tenant_id,
        ':pid': producto_id
      }
    };

    await dynamo.query(params).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'deleted item: ' + producto_id, })
    };
  } catch (err) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
