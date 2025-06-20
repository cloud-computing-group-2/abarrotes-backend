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
        url: '/dev/openapi.yaml',  // asegúrate que coincide con tu stage
        dom_id: '#swagger-ui',
      });
    };
  </script>
</body>
</html>
`;

module.exports.lambda_handler = async () => {
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
  const fs = require('fs');
  const path = require('path');
  const filePath = path.join(__dirname, 'openapi.yaml');

  try {
    const openapi = fs.readFileSync(filePath, 'utf8');
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/yaml',
        'Access-Control-Allow-Origin': '*',
      },
      body: openapi,
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: 'Error loading OpenAPI spec.',
    };
  }
};
