const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
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

    // Obtener body
    const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    const { tenant_id, nombre, precio, stock } = body;

    if (!tenant_id || !nombre || precio == null || stock == null) {
      throw new Error("Faltan campos requeridos: tenant_id, nombre, precio o stock");
    }

    // Validar token
    await validateToken(token, tenant_id);

    const existing = await dynamo.scan({
      TableName: tableName,
      FilterExpression: 'tenant_id = :t AND nombre = :n',
      ExpressionAttributeValues: {
        ':t': tenant_id,
        ':n': nombre
      },
      Limit: 1
    }).promise();

    if (existing.Items.length > 0) {
      throw new Error("Ya existe un producto con ese nombre en este tenant");
    }


    // Insertar producto
    const producto_id = uuidv4();
    const item = {
      producto_id,
      tenant_id,
      nombre,
      precio,
      stock
    };

    await dynamo.put({
      TableName: tableName,
      Item: item
    }).promise();


    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Producto creado', producto_id })
    };

  } catch (err) {
    console.error("Error en creación:", err);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
