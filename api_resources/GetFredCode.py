from flask_restful import Resource
from flask import session
class RetrieveFREDCodeResource(Resource):
    def get(self):
        # You can retrieve the FRED code from the session or the database here
        fred_code = session.get('fred_code')
        if fred_code:
            return {'fred_code': fred_code}, 200
        else:
            return {'message': 'No FRED code available'}, 404
