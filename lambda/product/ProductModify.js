const AWS = require('aws-sdk');
const { validateToken } = require('./auth.js');

const dynamo = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
  try {
    const tableName = process.env.TABLE_PRODUCTOS;
    if (!tableName) throw new Error("Variable TABLE_PRODUCTOS no definida");

    const rawAuth = event.headers?.Authorization || event.headers?.authorization;
    if (!rawAuth || !rawAuth.startsWith("Bearer ")) {
      throw new Error("Token Authorization Bearer no proporcionado");
    }
    const token = rawAuth.replace("Bearer ", "").trim();

    const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    const { tenant_id, producto_id, ...updates } = body;

    if (!tenant_id || !producto_id) {
      throw new Error("Faltan campos obligatorios: tenant_id y producto_id");
    }

    // Validar token
    await validateToken(token, tenant_id);

    // Armar UpdateExpression
    let expr = "SET ";
    const names = {};
    const values = {};
    let first = true;

    for (const k in updates) {
      const attrName = `#${k}`;
      const attrValue = `:${k}`;

      if (!first) expr += ", ";
      expr += `${attrName} = ${attrValue}`;
      names[attrName] = k;
      values[attrValue] = updates[k];
      first = false;
    }

    if (first) throw new Error("No se proporcionaron campos para modificar");

    const params = {
      TableName: tableName,
      Key: {
        tenant_id,
        producto_id
      },
      UpdateExpression: expr,
      ExpressionAttributeNames: names,
      ExpressionAttributeValues: values,
      ReturnValues: 'ALL_NEW'
    };

    const result = await dynamo.update(params).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Producto modificado con éxito', item: result.Attributes })
    };

  } catch (err) {
    console.error("Error al modificar producto:", err);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
