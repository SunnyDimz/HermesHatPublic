import os
import requests
import logging
# fetching data from FRED API

fred_api=os.environ.get('FRED_API_KEY')
FRED_SERIES_ENDPOINT = "https://api.stlouisfed.org/fred/series?series_id={code}&api_key={fred_api}&file_type=json"
def fetch_metadata_from_fred(code):
    url = FRED_SERIES_ENDPOINT.format(code=code, fred_api=fred_api)
    logging.info(f"Fetching metadata from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to fetch metadata for {code}. Status code: {response.status_code}")
            return None
        metadata = response.json().get('seriess', [])[0]
        return metadata
    except Exception as e:
        logging.error(f"An error occurred while fetching metadata: {e}")
        return None
    
FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={fred_api}&file_type=json"
def fetch_data_from_fred(code, observation_start=None, observation_end=None, units=None):
    """
    Fetch data from FRED with the given code and optional parameters.
    """
    url = FRED_ENDPOINT.format(code=code, fred_api=fred_api)
    if observation_start:
        url += f"&observation_start={observation_start}"
    if observation_end:
        url += f"&observation_end={observation_end}"
    if units:
        url += f"&units={units}"
    logging.info(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to fetch data for {code}. Status code: {response.status_code} Text: {response.text}")
            return None

        data = response.json()
        if "error_message" in data:
            logging.error(data["error_message"])
        observations = data.get('observations', [])
        logging.info(f"Fetched {len(observations)} observations for {code}.")
        metadata = fetch_metadata_from_fred(code)
        if metadata:
            metadata_fields = {
                'id': metadata.get('id'),
                'realtime_start': metadata.get('realtime_start'),
                'realtime_end': metadata.get('realtime_end'),
                'title': metadata.get('title'),
                'frequency': metadata.get('frequency'),
                'units': metadata.get('units'),
                'seasonal_adjustment': metadata.get('seasonal_adjustment')
            }
            return observations, metadata_fields
        
    except requests.ConnectionError:
        print("Failed to connect to the server.")
        return None
    except requests.Timeout:
        print("The request timed out.")
        return None
    except requests.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None
    except ValueError:  # This will capture JSON decoding errors
        print("Error decoding the server response.")
        return None
  # Fetching metadata for series and title  

