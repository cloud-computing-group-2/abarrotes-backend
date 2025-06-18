const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = 'ab_productos';

exports.handler = async (event) => {
  try {
    const token = headers.Authorization || headers.authorization
    body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body
    const { tenant_id, nombre, precio, stock } = body;
    await validateToken(token, tenant_id);

    const producto_id = uuidv4();
    const item = {
      producto_id,
      tenant_id,
      nombre,
      precio,
      stock
    };

    await dynamo.put({ TableName: tableName, Item: item }).promise();

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
