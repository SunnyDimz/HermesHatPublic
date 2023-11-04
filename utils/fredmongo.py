from models.models import BlogPost, FredData, mongo, db
from flask import Flask, jsonify, request, session, g, render_template
import json
import requests
import logging
import os
from api_resources.EconomicsChatResource import *
from utils.fred_utils import *
fred_api 
FRED_ENDPOINT
def fetch_data_from_fred_and_save_to_db(file_path, observation_start=None, observation_end=None, units=None):
    with open(file_path, 'r') as file:
        codes = json.load(file)
    
    for code in codes:
        fetched_data = fetch_data_from_fred(code, observation_start, observation_end, units)
        
        if fetched_data:
            observations = fetched_data.get('observations', [])
            logging.info(f"Fetched {len(observations)} observations for {code}.")
            
            # Create a FredData object based on fetched data and your model
            fred_entry = FredData(
                code=code,
                realtime_start=fetched_data.get("realtime_start"),
                realtime_end=fetched_data.get("realtime_end"),
                observation_start=fetched_data.get("observation_start"),
                observation_end=fetched_data.get("observation_end"),
                units=fetched_data.get("units"),
                count=fetched_data.get("count"),
                observations=observations  # This assumes your FredData model has an 'observations' field
            )
            
            # Save to MongoDB
            fred_entry.save_to_mongo()
            logging.info(f"Saved {len(observations)} observations for {code} to MongoDB.")
        else:
            logging.warning(f"Failed to fetch data for {code}. Skipping database save.")
