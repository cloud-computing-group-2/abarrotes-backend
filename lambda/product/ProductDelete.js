const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = 'ab_productos';

exports.handler = async (event) => {
  try {
    const token = event.headers.Authorization || event.headers.authorization
    body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body
    const { tenant_id, producto_id } = body;
    await validateToken(token, tenant_id);

    const params = {
        TableName: tableName,
        Key: {
          tenant_id: tenant_id,
          producto_id: producto_id
        }
      };

    await dynamo.delete(params).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Producto creado', producto_id })
    };
  } catch (err) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
