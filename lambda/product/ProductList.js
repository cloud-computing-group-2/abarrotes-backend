const AWS = require('aws-sdk');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = 'ab_productos';

exports.handler = async (event) => {
  try {
    const token = event.headers.Authorization || event.headers.authorization
    const tenant_id = event.queryStringParameters?.tenant_id;
    const limit = parseInt(event.queryStringParameters?.limit) || 10
    const nextToken = event.queryStringParameters?.nextToken

    body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body
    await validateToken(token, tenant_id);

    const params = {
      TableName: tableName,
      KeyConditionExpression: 'tenant_id = :tid AND producto_id = :pid',
      ExpressionAttributeValues: {
        ':tid': tenant_id
      },
      limit: limit
    };

    if (nextToken) {
        params.ExclusiveStartKey = JSON.parse(Buffer.from(nextToken, 'base64').toString('utf8'));
    }

    var list = await dynamo.query(params).promise();
    const response = {
        items: list.Items,
        nextToken: result.LastEvaluatedKey
          ? Buffer.from(JSON.stringify(result.LastEvaluatedKey)).toString('base64')
          : null
      };

    return {
      statusCode: 200,
      body: JSON.stringify(response)
    };
  } catch (err) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
