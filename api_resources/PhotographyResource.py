from flask_restful import Resource
from utils.aws_utils import fetch_s3_images  # Import the fetch_s3_images function
import logging

logger = logging.getLogger('root')
class PhotographyResource(Resource):
    def get(self):
        try:
            object_keys = fetch_s3_images()  # Calling the utility function
            return {'object_keys': object_keys}, 200
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {'message': 'An unexpected error occurred'}, 500
