from flask_restful import Resource, reqparse
from utils.fred_utils import fetch_data_from_fred  # Importing the fetch_data_from_fred function
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
import logging

logger = logging.getLogger('root')
def fetch_and_transform_data(code):
    observations = fetch_data_from_fred(code)
    if observations:
        return pd.DataFrame(observations)
    else:
        logger.warning(f"Failed to fetch data for code: {code}")
        return None

def create_plot(data, code):
    trace = go.Scatter(
        x=data['date'],
        y=data['value'],
        mode='lines',
        line=dict(color='#1f77b4', width=2.5)
    )

    layout = {
        'title': code,
        'xaxis': {
            'title': 'Time',
            'linecolor': 'black',
            'linewidth': 1,
            'mirror': True
        },
        'yaxis': {
            'title': 'Value',
            'linecolor': 'black',
            'linewidth': 1,
            'mirror': True
        },
        'plot_bgcolor': "#F5F5F5",
        'paper_bgcolor': "#E5E5E5",
    }
    fig = go.Figure(data=[trace], layout=layout)
    return plot(fig, output_type='div')

class EconomicsResource(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('fred_code', type=str, required=True, help="FRED code is required.")  # Corrected argument name
            args = parser.parse_args()

            fred_code = args['fred_code']
            data = fetch_and_transform_data(fred_code)
            if data is not None:
                plot_div = create_plot(data, fred_code)
                return {'plot_div': plot_div}, 200
            else:
                return {'message': f'No data found for FRED code {fred_code}'}, 404
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {'message': 'An unexpected error occurred'}, 500
