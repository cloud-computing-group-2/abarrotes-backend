
const AWS = require('aws-sdk');

const lambda = new AWS.Lambda();

const ENV = process.env.STAGE || 'dev';

async function validateToken(token, tenant_id) {
  if (!token || !tenant_id) {
    throw new Error('Token inválido o expirado');
  }

  const payload = { token, tenant_id };
  const params = {
    FunctionName: `abarrotes-usuarios-${ENV}-validar`,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify(payload)
  }

  var res = await lambda.invoke(params).promise();
  print(res)
  const result = JSON.parse(res.Payload);
  print(result)

  if (result.statusCode === 403) {
    throw new Error('Token inválido o expirado');
  }
  return true;
}

module.exports = {
  validateToken
};
