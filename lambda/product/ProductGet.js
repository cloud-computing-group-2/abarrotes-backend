const AWS = require('aws-sdk');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = 'ab_productos';

exports.handler = async (event) => {
  try {
    const token = event.headers.Authorization || event.headers.authorization
    const { tenant_id, producto_id } = event.queryStringParameters || {};
    await validateToken(token, tenant_id);

    const params = {
      TableName: tableName,
      KeyConditionExpression: 'tenant_id = :tid AND producto_id = :pid',
      ExpressionAttributeValues: {
        ':tid': tenant_id,
        ':pid': producto_id
      }
    };

    const result = await dynamo.query(params).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({
        items: result.Items
      })
    };
  } catch (err) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
