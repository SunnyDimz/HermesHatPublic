from api_resources import *
from config import app
import logging

logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)