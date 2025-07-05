const fs = require('fs');
const path = require('path');

module.exports.lambda_handler = async () => {
  const html = `
  <!DOCTYPE html>
  <html>
  <head>
    <title>Abarrotes Productos API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
      window.onload = () => {
        SwaggerUIBundle({
          url: '/dev/openapi.yaml',
          dom_id: '#swagger-ui',
        });
      };
    </script>
  </body>
  </html>
  `;
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'text/html',
      'Access-Control-Allow-Origin': '*',
    },
    body: html,
  };
};

module.exports.openapi_handler = async () => {
  const filePath = path.join(__dirname, '../openapi.yaml');
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/yaml',
        'Access-Control-Allow-Origin': '*',
      },
      body: content,
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: 'Error loading OpenAPI spec.',
    };
  }
};
