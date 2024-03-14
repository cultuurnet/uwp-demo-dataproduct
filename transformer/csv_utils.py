import csv
import sys
from datetime import datetime, timezone

def compare_input_with_latest_date(output_csv_path, latest_date, data_type):
    latest_date = datetime.fromisoformat(latest_date)
    latest_date = latest_date.astimezone(timezone.utc)
    with open(output_csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse the ISO 8601 timestamp format with timezone information
            entity_modified = datetime.fromisoformat(row[f'{data_type}_modifieddate'])
            print(f"entity_modified: {entity_modified}, latest_date: {latest_date}")
            if entity_modified <= latest_date:
                print("All entities from source file processed")
                sys.exit()  # Stop execution
