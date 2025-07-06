const AWS = require('aws-sdk');
const lambda = new AWS.Lambda();

const ENV = process.env.STAGE || 'dev';

async function validateToken(token, tenant_id) {
  if (!token || !tenant_id) {
    throw new Error('Token inválido o expirado');
  }

  const payload = {
    body: JSON.stringify({
      token,
      tenant_id
    })
  };

  const params = {
    FunctionName: `abarrotes-usuarios-${ENV}-validar`,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify(payload)
  };

  try {
    const res = await lambda.invoke(params).promise();
    const result = JSON.parse(res.Payload);
    console.log("validateToken result:", result);

    if (result.statusCode === 403) {
      throw new Error('Token inválido o expirado');
    }

    return true;
  } catch (err) {
    console.error("validateToken error:", err);
    throw new Error('Error al validar token');
  }
}

module.exports = {
  validateToken
};
