const { Client } = require('@opensearch-project/opensearch');
const AWS = require('aws-sdk');

const ES_ENDPOINT = process.env.ES_ENDPOINT;
const INDEX_NAME = process.env.INDEX_NAME;

// Cliente se conecta por HTTP sin SSL
const client = new Client({
  node: ES_ENDPOINT,
  ssl: {
    rejectUnauthorized: false  // no necesario si usas HTTP, pero no hace daño
  }
});

exports.handler = async (event) => {
  const bulkBody = [];

  for (const record of event.Records) {
    if (record.eventName !== 'INSERT' && record.eventName !== 'MODIFY') continue;

    const newImage = AWS.DynamoDB.Converter.unmarshall(record.dynamodb.NewImage);

    bulkBody.push({ index: { _index: INDEX_NAME, _id: `${newImage.tenant_id}_${newImage.producto_id}` } });
    bulkBody.push(newImage);
  }

  if (bulkBody.length > 0) {
    try {
      const response = await client.bulk({ refresh: true, body: bulkBody });
      console.log('Bulk insert result:', response.body);
    } catch (err) {
      console.error('Error inserting to Elasticsearch:', err);
    }
  }

  return { statusCode: 200 };
};
