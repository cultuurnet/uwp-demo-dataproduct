import csv
import sys
from datetime import datetime, timezone

def compare_input_date_with_latest_date(output_csv_path, latest_date, data_type):
    # latest_date is already a timezone-aware datetime object, no need to convert it
    with open(output_csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse the ISO 8601 timestamp format with timezone information
            input_date = datetime.fromisoformat(row[f'{data_type}_modifieddate'])

            print(f"input_date: {input_date}, fuseki_latest_date: {latest_date}")

            # Compare both as timezone-aware datetime objects
            if input_date <= latest_date:
                print("Stop condition: input_date <= latest_date. All entities from source file already processed")
                return True  # Stop condition met
    
    return False  # Continue with the next data type

