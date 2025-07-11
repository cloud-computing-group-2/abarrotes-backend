const { Client } = require('@opensearch-project/opensearch');
const { validateToken } = require('./auth.js');

const ES_ENDPOINT = process.env.ES_ENDPOINT;
const STAGE = process.env.STAGE;
const INDEX = `${STAGE}_ab_productos`;

// Cliente se conecta por HTTP sin SSL
const client = new Client({
  node: ES_ENDPOINT,
  ssl: {
    rejectUnauthorized: false  // no necesario si usas HTTP, pero no hace daño
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
    const tenant_id = query.tenant_id;
    const search = query.search;

    if (!tenant_id || !search) {
      throw new Error("Faltan tenant_id o search");
    }

    await validateToken(token, tenant_id);

    const result = await client.search({
      index: INDEX,
      body: {
        query: {
          bool: {
            must: [
              { match: { tenant_id } },
              {
                match: {
                  nombre: {
                    query: search,
                    fuzziness: "AUTO"
                  }
                }
              }
            ]
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
