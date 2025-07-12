const { Client } = require('@opensearch-project/opensearch');
const { validateToken } = require('./auth.js');

const ES_ENDPOINT = process.env.ES_ENDPOINT;
const STAGE = process.env.STAGE;
const INDEX = `${STAGE}_ab_productos`;

const client = new Client({
  node: ES_ENDPOINT,
  ssl: {
    rejectUnauthorized: false
  }
});

exports.handler = async (event) => {
  try {
    const rawAuth = event.headers?.Authorization || event.headers?.authorization;
    if (!rawAuth || !rawAuth.startsWith("Bearer ")) {
      throw new Error("Token Authorization Bearer no proporcionado");
    }
    const token = rawAuth.replace("Bearer ", "").trim();

    const query = event.queryStringParameters || {};
    const { tenant_id, ...searchParams } = query;

    if (!tenant_id || Object.keys(searchParams).length === 0) {
      throw new Error("Faltan tenant_id o parámetros de búsqueda");
    }

    await validateToken(token, tenant_id);

    const mustConditions = [{ match: { tenant_id } }];

    for (const [field, value] of Object.entries(searchParams)) {
      mustConditions.push({
        match: {
          [field]: {
            query: value,
            fuzziness: isNaN(value) ? "AUTO" : 0  // Fuzziness solo para strings
          }
        }
      });
    }

    const result = await client.search({
      index: INDEX,
      body: {
        query: {
          bool: {
            must: mustConditions
          }
        }
      }
    });

    const items = result.body.hits.hits.map(hit => hit._source);

    return {
      statusCode: 200,
      body: JSON.stringify({ items })
    };
  } catch (err) {
    console.error("Search error:", err);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: err.message })
    };
  }
};
