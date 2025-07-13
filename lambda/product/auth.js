const AWS = require('aws-sdk');
const lambda = new AWS.Lambda();

const ENV = process.env.STAGE || 'dev';

async function validateToken(token, tenant_id) {
  if (!token || !tenant_id) {
    throw new Error('Token inválido o expirado');
  }

  const payload = {
    body: JSON.stringify({ token, tenant_id })
  };

  const params = {
    FunctionName: `abarrotes-usuarios-${ENV}-validar`,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify(payload)
  };

  try {
    const res = await lambda.invoke(params).promise();
    const result = JSON.parse(res.Payload);

    if (result.statusCode !== 200) {
      throw new Error('Token inválido o expirado');
    }

    return true;
  } catch (err) {
    console.error("validateToken error:", err);
    throw new Error('Error al validar token');
  }
}

async function validateAdmin(token, tenant_id) {
  if (!token || !tenant_id) {
    throw new Error('Token inválido o expirado');
  }

  const payload = {
    body: JSON.stringify({ token, tenant_id })
  };

  const params = {
    FunctionName: `abarrotes-usuarios-${ENV}-admin`,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify(payload)
  };

  try {
    const res = await lambda.invoke(params).promise();
    const result = JSON.parse(res.Payload);

    if (result.statusCode !== 200) {
      throw new Error('Acceso restringido');
    }

    // Parsear el body si está presente
    const resultBody = typeof result.body === 'string'
      ? JSON.parse(result.body)
      : result.body;

    return {
      success: true,
      user_id: resultBody.user_id,
      rol: resultBody.rol
    };
  } catch (err) {
    console.error("validateAdmin error:", err);
    throw new Error('Error al validar admin');
  }
}

module.exports = {
  validateToken,
  validateAdmin
};
