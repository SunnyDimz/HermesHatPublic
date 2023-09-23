from flask import Flask
from flask_compress import Compress
from flask_caching import Cache
from flask_mail import Mail
import logging

application = Flask(__name__)
Compress(application)
logging.basicConfig(level=logging.DEBUG)

# Cache configuration
application.config['CACHE_TYPE'] = 'simple'
application.config['CACHE_DEFAULT_TIMEOUT'] = 3600  # 1 hour default timeout

cache = Cache(application)
mail = Mail(application)
