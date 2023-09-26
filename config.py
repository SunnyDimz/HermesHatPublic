from flask import Flask
from flask_compress import Compress
from flask_caching import Cache
from flask_mail import Mail
import logging
from flask_socketio import SocketIO

app = Flask(__name__)
Compress(app)
socketio = SocketIO(app)
logging.basicConfig(level=logging.DEBUG)

# Cache configuration
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600  # 1 hour default timeout

cache = Cache(app)
mail = Mail(app)
