from flask_restful import Resource
from flask import request, jsonify
import pandas as pd
import logging
from api_resources.EconomicsResource import create_plot  # Ensure this is the correct import for your plotting logic

logger = logging.getLogger('root')

class UpdateGraphResource(Resource):
    def post(self):
        try:
            # The data should be sent in the request's JSON body
            data = request.get_json()
            if data:
                # Convert the data to a pandas DataFrame
                df = pd.DataFrame(data)
                
                # Use the FRED code from the request to label the graph
                fred_code = request.args.get('code')

                # Create a plot using the data
                plot_div = create_plot(df, fred_code)

                # Return the plot div
                return jsonify({'plot_div': plot_div}), 200
            else:
                return {'message': 'No data provided'}, 400

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {'message': 'An unexpected error occurred'}, 500
