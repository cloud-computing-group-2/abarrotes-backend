import json

def lambda_handler(event, context):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Abarrotes Usuarios API Docs</title>
      <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        const ui = SwaggerUIBundle({
          url: '/openapi.yaml',
          dom_id: '#swagger-ui',
        });
      </script>
    </body>
    </html>
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": html_content
    }

def openapi_handler(event, context):
    with open("openapi.yaml", "r") as f:
        content = f.read()
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/yaml"
        },
        "body": content
    }
