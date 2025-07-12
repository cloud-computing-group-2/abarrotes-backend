const { Client } = require('@opensearch-project/opensearch');
const AWS = require('aws-sdk');

const ES_ENDPOINT = process.env.ES_ENDPOINT;
const INDEX_NAME = process.env.INDEX_NAME;

// Cliente se conecta por HTTP sin SSL
const client = new Client({
  node: ES_ENDPOINT,
  ssl: {
    rejectUnauthorized: false
  }
});

exports.handler = async (event) => {
  const bulkBody = [];

  for (const record of event.Records) {
    let id;
    if (record.eventName === 'INSERT' || record.eventName === 'MODIFY') {
      const newImage = AWS.DynamoDB.Converter.unmarshall(record.dynamodb.NewImage);
      id = `${newImage.tenant_id}_${newImage.producto_id}`;

      bulkBody.push({ index: { _index: INDEX_NAME, _id: id } });
      bulkBody.push(newImage);
    }

    if (record.eventName === 'REMOVE') {
      const oldImage = AWS.DynamoDB.Converter.unmarshall(record.dynamodb.OldImage);
      id = `${oldImage.tenant_id}_${oldImage.producto_id}`;

      bulkBody.push({ delete: { _index: INDEX_NAME, _id: id } });
    }
  }

  if (bulkBody.length > 0) {
    try {
      const response = await client.bulk({ refresh: true, body: bulkBody });
      console.log('Bulk result:', JSON.stringify(response.body, null, 2));
    } catch (err) {
      console.error('Error executing bulk operation:', err);
    }
  }

  return { statusCode: 200 };
};
