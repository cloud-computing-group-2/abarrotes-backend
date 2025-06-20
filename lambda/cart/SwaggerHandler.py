import json
from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)


SWAGGER_URL = '/swagger' 
API_URL = './swagger.json'  

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Abarrotes Compras API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json')
def swagger_json():
    return send_from_directory('.', 'swagger.json')

def lambda_handler(event, context):
    return app(event, context)
