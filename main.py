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
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations(cafile=certifi.where())
# Endpoint for fetching data.
# Set the secret key from an environment variable
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
# Initialize logging
logging.basicConfig(level=logging.INFO)



if __name__ == '__main__':
    from api_resources.PhotographyResource import *
    from api_resources.BlogResource import *
    from api_resources.HomeResource import *
    from api_resources.MediaResource import *
    from api_resources.AboutResource import *
    from api_resources.EconomicsResource import *
    from api_resources.UpdateGraph import *
    from api_resources.SubmitAnswer import *
    from api_resources.ChatResource import *
    from api_resources.LoginResource import *
    from api_resources.YoutubeDetails import *
    from api_resources.MongoQuery import *
    from api_resources.EconomicsChatResource import * 
    from api_resources.GetFredCode import *
    api.add_resource(HomeResource, '/api/home')
    api.add_resource(BlogResource, '/api/blog')
    api.add_resource(PhotographyResource, '/api/photographs')
    api.add_resource(MediaResource, '/api/media')
    api.add_resource(AboutResource, '/api/about')
    api.add_resource(EconomicsResource, '/api/economics')
    api.add_resource(UpdateGraphResource, '/api/update_graph')
    api.add_resource(AnswerResource, '/api/submit_answer')
    api.add_resource(ChatGPTResource, '/api/chat')
    api.add_resource(LoginResource, '/api/login')
    api.add_resource(YouTubeDetailsResource, '/api/youtube_details')
    api.add_resource(EconomicsChatGPTResource, '/api/economics_chat')
    api.add_resource(MongoQueryResource, '/api/mongo_query')
    api.add_resource(RetrieveFREDCodeResource, '/api/get_fred_code')
    app.run(debug=True)
