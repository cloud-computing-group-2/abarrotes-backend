const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

const TABLE_AUTH = process.env.TABLE_AUTH;
const TABLE_USER = process.env.TABLE_USER;

/**
 * Verifica si el token es válido y no está expirado.
 */
async function validateToken(token, tenant_id, skip_tenant_check = false) {
  if (!token || !tenant_id) {
    throw new Error('Token inválido o tenant_id faltante');
  }

  const res = await dynamodb.get({
    TableName: TABLE_AUTH,
    Key: {
      token,
      tenant_id
    }
  }).promise();

  const item = res.Item;

  if (!item) {
    throw new Error('Token no existe');
  }

  if (!skip_tenant_check && item.tenant_id !== tenant_id) {
    throw new Error('Token no corresponde al tenant');
  }

  const now = new Date().toISOString();
  const expires = item.expires_at;

  if (now > expires) {
    throw new Error('Token expirado');
  }

  return true;
}

/**
 * Verifica si el token es válido y si el usuario tiene rol ADMIN.
 */
async function validateAdmin(token, tenant_id) {
  if (!token || !tenant_id) {
    return {
      success: false,
      statusCode: 403,
      error: 'Token o tenant_id faltante'
    };
  }

  // Paso 1: verificar token
  const authRes = await dynamodb.get({
    TableName: TABLE_AUTH,
    Key: {
      token,
      tenant_id
    }
  }).promise();

  const item = authRes.Item;
  if (!item) {
    return {
      success: false,
      statusCode: 403,
      error: 'Token no existe'
    };
  }

  const now = new Date().toISOString();
  if (now > item.expires_at) {
    return {
      success: false,
      statusCode: 403,
      error: 'Token expirado'
    };
  }

  if (item.tenant_id !== tenant_id) {
    return {
      success: false,
      statusCode: 403,
      error: 'Token no corresponde al tenant'
    };
  }

  const user_id = item.user_id;

  // Paso 2: verificar rol del usuario
  const userRes = await dynamodb.get({
    TableName: TABLE_USER,
    Key: {
      tenant_id,
      user_id
    }
  }).promise();

  if (!userRes.Item) {
    return {
      success: false,
      statusCode: 403,
      error: 'Usuario no encontrado'
    };
  }

  const rol = userRes.Item.rol;
  if (rol !== 'ADMIN') {
    return {
      success: false,
      statusCode: 403,
      error: 'Acceso restringido a administradores'
    };
  }

  return {
    success: true,
    user_id,
    rol
  };
}

module.exports = {
  validateToken,
  validateAdmin
};
