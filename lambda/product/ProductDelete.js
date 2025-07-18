const AWS = require('aws-sdk');
const { validateToken, validateAdmin } = require('./auth.js');

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

    // Parsear body
    const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    const { tenant_id, producto_id } = body;

    if (!tenant_id || !producto_id) {
      throw new Error("Faltan tenant_id o producto_id");
    }

    // Validar token
    await validateToken(token, tenant_id);
    // Validar admin
    const c = await validateAdmin(token, tenant_id);
    if (!c.success) {
      return {
        statusCode: c.statusCode || 403,
        body: JSON.stringify({ error: c.error || 'Acceso denegado' }),
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
      };
    }

    // Eliminar el producto
    const params = {
      TableName: tableName,
      Key: {
        tenant_id,
        producto_id
      }
    };

    await dynamo.delete(params).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Producto eliminado' }),
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      }
    }
    
  

  } catch (err) {
    console.error("Error al eliminar producto:", err);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message }),
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      }
    };
    
  }
};
