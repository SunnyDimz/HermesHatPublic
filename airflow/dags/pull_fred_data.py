from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import json
import logging
import requests
import pandas as pd
from pymongo import MongoClient
import os

# Define the default arguments for the DAG
default_args = {
    'owner': 'hermesadmin',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['d.borzhko@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=20),
}

# Define the DAG
dag = DAG(
    'pull_fred_data',
    default_args=default_args,
    description='DAG for pulling data from FRED API and saving to MongoDB',
    schedule_interval='@daily',
)

# Airflow Variable for API key and MongoDB connection details
fred_api = Variable.get('FRED_API_KEY')
mongo_conn_id = Variable.get('MONGO_CONN_ID')

# Define your FRED endpoints here
FRED_SERIES_ENDPOINT = "https://api.stlouisfed.org/fred/series?series_id={code}&api_key={fred_api}&file_type=json"
FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={fred_api}&file_type=json"

# Function to fetch metadata from FRED
def fetch_metadata_from_fred(code):
    url = FRED_SERIES_ENDPOINT.format(code=code, fred_api=fred_api)
    logging.info(f"Fetching metadata from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(response)
        if response.status_code != 200:
            logging.error(f"Failed to fetch metadata for {code}. Status code: {response.status_code}")
            return None
        metadata = response.json().get('seriess', [])[0]
        return metadata
    except Exception as e:
        logging.error(f"An error occurred while fetching metadata: {e}")
        return None

# Function to fetch data from FRED
def fetch_data_from_fred(code, observation_start=None, observation_end=None, units=None):
    url = FRED_ENDPOINT.format(code=code, fred_api=fred_api)
    if observation_start:
        url += f"&observation_start={observation_start}"
    if observation_end:
        url += f"&observation_end={observation_end}"
    if units:
        url += f"&units={units}"
    logging.info(f"Fetching data from URL: {url}")
    print(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data for {code}. Status code: {response.status_code}")
            print("Failed to fetch data for {code}. Status code: {response.status_code}")
            return None, None
        data = response.json()
        print("received data")
        if "error_message" in data:
            logging.error(data["error_message"])
            print(data["error_message"])
            return None, None
        observations = data.get('observations', [])
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
    except Exception as e:
        logging.error(f"An error occurred while fetching data: {e}")
        return None, None

# Function to validate FRED data with pandas
def validate_fred_data_with_pandas(observations):
    df = pd.DataFrame(observations)
    if df['date'].duplicated().any():
        logging.error("Validation Failed: Duplicate dates found.")
        return False
    if df['value'].isna().any():
        logging.error("Validation Failed: Missing values found.")
        return False
    return True

# Function to save data to MongoDB
def save_to_mongo(observations, metadata, code):
    try:
        # Assuming that mongo_conn_id is a valid MongoDB connection URI
        client = MongoClient(mongo_conn_id)
        print("Connected to MongoDB.")
        db = client['fred_data']
        collection = db['data']
        for observation in observations:
            observation.update(metadata)
            collection.update_one({'id': observation['id']}, {'$set': observation}, upsert=True)
        logging.info(f"Saved data for {code} to MongoDB.")
    except Exception as e:
        logging.error(f"Failed to save data for {code} to MongoDB: {e}")

# Task to fetch, validate, and save FRED data
def fetch_validate_and_save_fred_data():
    fred_codes = Variable.get('fred_codes', deserialize_json=True)
    print(fred_codes)
    for code in fred_codes:
        observations, metadata = fetch_data_from_fred(code)
        print(observations)
        if observations and metadata and validate_fred_data_with_pandas(observations):
            save_to_mongo(observations, metadata, code)
        else:
            logging.warning(f"Data for {code} did not pass validation or was not fetched.")

# Define the PythonOperator to execute the task for fetching, validating, and saving FRED data
fetch_validate_and_save_fred_data_task = PythonOperator(
    task_id='fetch_validate_and_save_fred_data',
    python_callable=fetch_validate_and_save_fred_data,
    dag=dag,
)
fetch_validate_and_save_fred_data_task
# Since we have only one task, no need for task ordering
