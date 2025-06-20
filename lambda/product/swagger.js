module.exports.lambda_handler = async (event) => {
    const stage = event.requestContext.stage;
    const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Abarrotes Productos API Docs</title>
      <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        const ui = SwaggerUIBundle({
          url: '/${stage}/openapi.yaml',
          dom_id: '#swagger-ui',
        });
      </script>
    </body>
    </html>
    `;
    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        body: html
    };
};

module.exports.openapi_handler = async () => {
    const fs = require('fs');
    const yaml = fs.readFileSync('openapi.yaml', 'utf8');
    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/yaml',
            'Access-Control-Allow-Origin': '*'
        },
        body: yaml
    };
};
