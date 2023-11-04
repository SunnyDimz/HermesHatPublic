from flask import Flask
from flask_restful import Api
import logging
import os
import certifi
import ssl
import urllib3
from web_routes import *

# Initialize Flask
app = Flask(__name__)
api = Api(app)

# Secure HTTP client setup
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations(cafile=certifi.where())

# Set the secret key for the Flask app
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Register API resources with abstracted paths and resource names
if __name__ == '__main__':
    # Import resources with generic names
    from api_resources.GenericResource1 import *
    from api_resources.GenericResource2 import *
    # ... other resources
    
    # Add resources to the API with generic endpoint names
    api.add_resource(GenericResource1, '/api/resource1')
    api.add_resource(GenericResource2, '/api/resource2')
    # ... other resource endpoints
    
    # Run the application
    app.run(debug=True)
