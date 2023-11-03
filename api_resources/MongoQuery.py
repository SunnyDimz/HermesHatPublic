from flask_restful import Resource, reqparse
from pymongo import MongoClient
import logging
from models.models import FredData, mongo, db


# Initialize logging
logging.basicConfig(level=logging.INFO)

class MongoQueryResource(Resource):
    collection = mongo.db.fred_data

    def get(self, fred_code):
        # Query MongoDB for the given FRED code
        query_result = self.collection.find_one({"fred_code": fred_code})

        if query_result:
            logging.info(f"Data found for FRED code: {fred_code}")
            return {'status': 'Data found', 'data': query_result}, 200
        else:
            logging.info(f"No data found for FRED code: {fred_code}")
            return {'status': 'No data found'}, 404
