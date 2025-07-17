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
    // Preflight CORS
    if (event.httpMethod === 'OPTIONS') {
      return {
        statusCode: 200,
        headers: CORS_HEADERS,
        body: ''
      };
    }

    const tableName = process.env.TABLE_PRODUCTOS;
    if (!tableName) throw new Error("Variable de entorno TABLE_PRODUCTOS no definida");

    const rawAuth = event.headers?.Authorization || event.headers?.authorization;
    if (!rawAuth || !rawAuth.startsWith("Bearer ")) {
      throw new Error("Token Authorization Bearer no proporcionado");
    }
    const token = rawAuth.replace("Bearer ", "").trim();

    const tenant_id = event.queryStringParameters?.tenant_id;
    if (!tenant_id) {
      throw new Error("Falta 'tenant_id' en los parámetros de la query");
    }

    // Leer y validar paginación
    const limit = parseInt(event.queryStringParameters?.limit, 10) || 10;
    if (limit <= 0 || isNaN(limit)) throw new Error("El parámetro 'limit' debe ser un número positivo");

    const nextToken = event.queryStringParameters?.nextToken;

    // Consulta paginada por tenant_id
    const params = {
      TableName: tableName,
      KeyConditionExpression: 'tenant_id = :tid',
      ExpressionAttributeValues: { ':tid': tenant_id },
      Limit: limit,
    };

    if (nextToken) {
      try {
        params.ExclusiveStartKey = JSON.parse(
          Buffer.from(nextToken, 'base64').toString('utf8')
        );
      } catch (e) {
        throw new Error("Token de paginación inválido");
      }
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
