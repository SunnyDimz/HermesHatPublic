from airflow import DAG
import os
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.fredmongo import fetch_data_from_fred_and_save_to_db  # Import your function
import sys
from airflow.models import Variable



default_args = {
    'owner': 'hermesadmin',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'provide_context': True,  # Important for passing file paths and other variables
}

dag = DAG(
    'economics_data_pipeline',
    default_args=default_args,
    description='Pipeline for economics data processing',
    schedule_interval='@daily',  # Run weekly as per your requirement
)

