import os
import requests
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO)

# A class to interact with the FRED API
class FredAPI:
    # Base URL for FRED API
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    # Initialize with API key from environment variables
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY')

    # Private method to perform API requests
    def _make_request(self, endpoint, params):
        # ... Code to make a request to the FRED API ...
        pass

    # Fetch series metadata from FRED
    def fetch_metadata(self, series_id):
        # ... Code to fetch and return metadata ...
        pass

    # Fetch series observations from FRED
    def fetch_observations(self, series_id, **kwargs):
        # ... Code to fetch and return observations ...
        pass

# Example of how to use the FredAPI class
if __name__ == "__main__":
    fred_api = FredAPI()
    # Example call to fetch observations, with series ID and optional params
    observations, metadata = fred_api.fetch_observations('GDP', observation_start='2020-01-01')
    # Handle the fetched data
    # ...
