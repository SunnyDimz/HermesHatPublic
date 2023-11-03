import pandas as pd
import logging
from flask import session
from utils.fred_utils import fetch_data_from_fred
def validate_fred_data_with_pandas(observations):
    # Convert observations to DataFrame
    df = pd.DataFrame(observations)
    
    # 1. Check for Duplicate Dates
    if df['date'].duplicated().any():
        logging.error("Validation Failed: Duplicate dates found.")
        return False
    
    # 2. Check for Missing Values
    if df['value'].isna().any():
        logging.error("Validation Failed: Missing values found.")
        return False
    
    return True

def main():
    # Your code to fetch the fred_code from EconomicsChatGPTResource
    fred_code = session['chat_history'][-1]['fred_code']
    
    if fred_code:
        observations, metadata_fields = fetch_data_from_fred(fred_code)
        if observations:
            is_valid = validate_fred_data_with_pandas(observations)
            if is_valid:
                print("Data is valid. Proceeding to the next steps.")
            else:
                print("Data validation failed.")
