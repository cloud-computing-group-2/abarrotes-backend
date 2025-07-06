const AWS = require('aws-sdk');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
  try {
    const tableName = process.env.TABLE_PRODUCTOS;
    if (!tableName) throw new Error("Variable TABLE_PRODUCTOS no definida");

    // Obtener token desde cabecera Authorization
    const rawAuth = event.headers?.Authorization || event.headers?.authorization;
    if (!rawAuth || !rawAuth.startsWith("Bearer ")) {
      throw new Error("Token Authorization Bearer no proporcionado");
    }
    const token = rawAuth.replace("Bearer ", "").trim();

    // Obtener parámetros de la URL
    const { tenant_id, producto_id } = event.queryStringParameters || {};
    if (!tenant_id || !producto_id) {
      throw new Error("Faltan tenant_id o producto_id en query");
    }

    // Validar token
    await validateToken(token, tenant_id);

    // Obtener el producto
    const params = {
      TableName: tableName,
      Key: {
        tenant_id,
        producto_id
      }
    };
    console.log("params:", params)

    const result = await dynamo.get(params).promise();
    console.log("result:", result)

    if (!result.Item) {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: "Producto no encontrado" })
      };
    }

    return {
      statusCode: 200,
      body: JSON.stringify(result.Item)
    };

  } catch (err) {
    console.error("Error al buscar producto:", err);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
