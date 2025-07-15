const AWS = require('aws-sdk');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type,Authorization',
  'Access-Control-Allow-Methods': 'GET,OPTIONS,POST,PUT,DELETE',
};

exports.handler = async (event) => {
  try {
    // Responder preflight CORS
    if (event.httpMethod === 'OPTIONS') {
      return {
        statusCode: 200,
        headers: CORS_HEADERS,
        body: ''
      };
    }

    const tableName = process.env.TABLE_PRODUCTOS;
    if (!tableName) throw new Error("Variable TABLE_PRODUCTOS no definida");

    const rawAuth = event.headers?.Authorization || event.headers?.authorization;
    if (!rawAuth || !rawAuth.startsWith("Bearer ")) {
      throw new Error("Token Authorization Bearer no proporcionado");
    }
    const token = rawAuth.replace("Bearer ", "").trim();

    const tenant_id = event.queryStringParameters?.tenant_id;
    if (!tenant_id) {
      throw new Error("Falta tenant_id en query");
    }

    // Validar token (lanza error si no coincide con tenant_id)
    await validateToken(token, tenant_id);

    const limit = parseInt(event.queryStringParameters?.limit) || 10;
    const nextToken = event.queryStringParameters?.nextToken;

    // Usamos query (con índice por tenant_id) y paginación
    const params = {
      TableName: tableName,
      KeyConditionExpression: 'tenant_id = :tid',
      ExpressionAttributeValues: { ':tid': tenant_id },
      Limit: limit,
    };
    if (nextToken) {
      params.ExclusiveStartKey = JSON.parse(
        Buffer.from(nextToken, 'base64').toString('utf8')
      );
    }

    const result = await dynamo.query(params).promise();

    const response = {
      items: result.Items,
      nextToken: result.LastEvaluatedKey
        ? Buffer.from(JSON.stringify(result.LastEvaluatedKey)).toString('base64')
        : null
    };

    return {
      statusCode: 200,
      headers: CORS_HEADERS,
      body: JSON.stringify(response)
    };

  } catch (err) {
    console.error("Error al listar productos:", err);
    return {
      statusCode: 400,
      headers: CORS_HEADERS,
      body: JSON.stringify({ error: err.message })
    };
  }
};
