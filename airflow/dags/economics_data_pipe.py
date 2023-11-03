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

def pull_and_save_fred_data(**kwargs):
    
    file_path = kwargs.get('file_path', '/Users/dimz/EconWizard/utils/fred_codes.json')  # Replace with the correct path
    fetch_data_from_fred_and_save_to_db(file_path)

t1 = PythonOperator(
    task_id='pull_and_save_fred_data',
    python_callable=pull_and_save_fred_data,
    op_kwargs={'file_path': '/Users/dimz/EconWizard/utils/fred_codes.json'},  # Pass the file path to your JSON file here
    dag=dag,
)

# Define other tasks and their dependencies as needed

t1  # Assuming this is the first task to run
