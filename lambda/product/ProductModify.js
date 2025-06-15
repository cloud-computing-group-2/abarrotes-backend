const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = 'ab_productos';

exports.handler = async (event) => {
  try {
    body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body
    const { token, tenant_id, producto_id, ...updates } = body;
    await validateToken(token, tenant_id);

    let expr = "set";
    let names = {};
    let values = {};
    let prefix = " ";
    for (var k in updates) {
        const attrName  = `#${k}`
        const attrValue = `:${k}`

        expr += `${prefix}{attrName} = {attrValue}`
        names[attrName] = k
        names[attrValue] = attrValue

        prefix = ', ';
    }

    const params = {
        TableName: tableName,
        Key: {
          tenant_id,
          producto_id
        },
        UpdateExpression: expr,
        ExpressionAttributesNames: names,
        ExpressionAttributesValues: values,
        ReturnValues: 'ALL_NEW',
      };

    await dynamo.update(params).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Producto eliminado:' + producto_id })
    };
  } catch (err) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
