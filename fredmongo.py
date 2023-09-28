from models import BlogPost, FredData, mongo
from flask import Flask, jsonify, request, session, g, render_template
import requests
import logging
codes=['UNRATE', 'CIVPART', 'EMRATIO','FEDFUNDS', 'GS10', 'DTWEXB', 'NETFI', 'GFDEBTN', 'HOUST','T10Y2Y']
FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key=5c78bd237c041fcf6bebdae4f8e05905&file_type=json"
def fetch_data_from_fred(code, observation_start=None, observation_end=None, units=None):
    """
    Fetch data from FRED with the given code and optional parameters.
    """
    url = FRED_ENDPOINT.format(code=code)
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
        return data
        
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

def fetch_data_from_fred_and_save_to_db(code, observation_start=None, observation_end=None, units=None):
    fetched_data = fetch_data_from_fred(code, observation_start, observation_end, units)
    logging.info(f"Fetched {len(fetched_data)} observations for {code}.")
    if fetched_data:
        logging.info(f"Saving {len(fetched_data)} observations for {code} to MongoDB.")
        fred_entry = FredData(
            code=code,
            realtime_start=fetched_data.get("realtime_start"),
            realtime_end=fetched_data.get("realtime_end"),
            observation_start=fetched_data.get("observation_start"),
            observation_end=fetched_data.get("observation_end"),
            units=fetched_data.get("units"),
            count=fetched_data.get("count"),
            observations=fetched_data.get("observations")
        )
        fred_entry.save_to_mongo()

for code in codes:
    fetch_data_from_fred_and_save_to_db(code)
