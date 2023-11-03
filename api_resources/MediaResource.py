import logging
from flask_restful import Resource

logger = logging.getLogger('root')
class MediaResource(Resource):
    def get(self):
        try:
            # Simply return a message as no data is passed in the original implementation
            return {'message': 'Media content rendered'}, 200
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {'message': 'An unexpected error occurred'}, 500
