import jwt
from config import app
import logging
def verify_jwt(token):
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        logging.error("Invalid token.")
        return None