const AWS = require('aws-sdk');
const lambda = new AWS.Lambda();

const ENV = process.env.STAGE || 'dev';

async function validateToken(token, tenant_id, skip_tenant = false) {
  if (!token || !tenant_id) {
    throw new Error('Token inválido o expirado');
  }

  const payload = {
    body: JSON.stringify({ token, tenant_id, skip_tenant })
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
    return {
      success: false,
      statusCode: 403,
      error: 'Token o tenant_id faltante'
    };
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

    // Parsear el body de la respuesta
    let message;
    try {
      const parsed = JSON.parse(result.body);
      message = typeof parsed === 'string' ? parsed : parsed.error || parsed.message;
    } catch (e) {
      message = result.body; // body sin parsear
    }

    if (result.statusCode !== 200) {
      return {
        success: false,
        statusCode: result.statusCode,
        error: message || 'Acceso restringido'
      };
    }

    return {
      success: true,
      user_id: message?.user_id, // por si el mensaje incluye esto
      rol: message?.rol
    };
  } catch (err) {
    console.error("validateAdmin error:", err);
    throw new Error("Accesso restringido") // fuck handling errors
  }
}

module.exports = {
  validateToken,
  validateAdmin
};
