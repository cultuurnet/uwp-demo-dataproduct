# Table of Contents
- [Main Script](#main-script)
	- [Features](#features)
	- [Usage](#usage)
	- [Example Usage](#example-usage)
	- [Dependencies](#dependencies)
- [Fuseki Client](#fuseki-client)
	- [Features](#features-1)
	- [Usage](#usage-1)
		- [Authentication Configuration](#authentication-configuration)
		- [Querying](#querying)
		- [Data Upload](#data-upload)
		- [Graph Management](#graph-management)
	- [Error Handling](#error-handling)
	- [Example Usage](#example-usage-1)
	- [Dependencies](#dependencies-1)
- [Fuseki Date Extraction](#fuseki-date-extraction)
	- [Features](#features-2)
	- [Usage](#usage-2)
		- [Latest Update Extraction](#latest-update-extraction)
		- [Datetime Transformation](#datetime-transformation)
	- [Example Usage](#example-usage-2)
	- [Dependencies](#dependencies-2)
- [RDF Utilities](#rdf-utilities)
	- [Features](#features-3)
	- [Usage](#usage-3)
		- [RDF Graph Generation](#rdf-graph-generation)
	- [Example Usage](#example-usage-3)
	- [Dependencies](#dependencies-3)
- [CSV Utilities](#csv-utilities)
	- [Features](#features-4)
	- [Usage](#usage-4)
	- [Example Usage](#example-usage-4)
	- [Dependencies](#dependencies-4)

  
# Main Script

The `main.py` script orchestrates the process of pushing data to a Fuseki server after transforming and processing it.

## Features

- **Push Data to Fuseki**: It pushes data to the Fuseki server by performing the following steps:
    1. **Retrieve Latest Modified Date**: Finds the latest modified date in the Fuseki database using the `get_latest_fuseki_update` function from the `fuseki_date_extraction` module.
    2. **Compare Input Data**: Compares the input data (CSV file) with the latest modified date to determine if there are new entities to process.
    3. **Generate RDF Graph**: Generates an RDF graph (N-Quads) from the CSV data using the YARRRML mapping files with the `generate_rdf_graph` function from the `rdf_utils` module.
    4. **Clear Existing Graphs**: Clears existing named entity graphs in the Fuseki server using the `clear_graphs` method of the `FusekiClient` class from the `fuseki_client` module.
    5. **Load RDF Graph**: Loads the generated RDF graph (N-Quads) into the Fuseki server using the `load_store` method of the `FusekiClient` class.

## Usage

1. Ensure that the required dependencies and modules (`fuseki_client`, `fuseki_date_extraction`, `rdf_utils`, `csv_utils`, `constants`) are available in the project directory.
2. Run the `main.py` script.

## Example Usage
Run the main.py script using the CLI tool with:
```bash
dp run
```

## Dependencies

- `logging`: Standard library module for logging.
- `FusekiClient`: Custom client class for interacting with the Fuseki server.
- `get_latest_fuseki_update`: Function for retrieving the latest modified date from the Fuseki database for each specific entity type.
- `generate_rdf_graph`: Function for generating an RDF graph from CSV data.
- `compare_input_with_latest_date`: Function for comparing input data timestamps with the latest modified date in Fuseki.
- `constants`: Module containing constant values used in the script.

# Fuseki Client

The `FusekiClient` is a Python client for interacting with a Fuseki server, which is a SPARQL server used for querying and updating RDF data.

## Features

- **SPARQL Querying**: Execute SPARQL queries against the Fuseki server.
- **Data Upload**: Upload RDF data to the Fuseki server.
- **Graph Management**: Clear graphs or load datasets into the Fuseki server.
- **OAuth2 Authentication**: Provides OAuth2 authentication support for secure access to the Fuseki server.

## Usage

To use the `FusekiClient`, you first need to configure the authentication credentials and server endpoint. Then, you can perform various operations such as querying, data upload, and graph management.

### Authentication Configuration

You need to provide OAuth2 authentication credentials to authenticate with the Fuseki server. These credentials include the client ID, client secret, and authentication token URL.

### Querying

You can execute SPARQL queries against the Fuseki server using the `query` method of the `FusekiClient`. The method takes a SPARQL query string as input and returns the query result in JSON format.

### Data Upload

To upload RDF data to the Fuseki server, you can use the `write_graph` method. This method accepts an RDF dataset and uploads it to the server. Note that the dataset should be in N-Quads format.

### Graph Management

The `clear_graphs` method allows you to clear graphs in the Fuseki server corresponding to a provided dataset. You can also load a dataset into the server using the `load_store` method.

## Error Handling

The `FusekiClient` provides error handling for various scenarios, such as invalid tokens or failed requests. It retries requests after token refresh if an invalid token error occurs.

## Example Usage

```python
from tools.fuseki_client import FusekiClient

# Initialize the FusekiClient with authentication credentials
client = FusekiClient(output_port_name="fuseki_output_port")

# Execute a SPARQL query
query = "SELECT ?subject ?predicate ?object WHERE {?subject ?predicate ?object}"
result = client.query(query)
print(result)

# Upload RDF data
data = "<http://example.org/subject> <http://example.org/predicate> <http://example.org/object> ."
client.write_graph(data)

# Clear graphs
client.clear_graphs(dataset)

# Load dataset
client.load_store(graph)
```

## Dependencies

- `httpx`: Python HTTP client library for making HTTP requests.
- `authlib`: Library for OAuth2 authentication support.
- `pyoxigraph`: Library for RDF data handling.
- `rdflib`: Library for working with RDF data.
- `dateutil`: Library for parsing ISO 8601 timestamps.
- `tools`: Custom tools module for environment variable retrieval.

# Fuseki Date Extraction

The `fuseki_date_extraction.py` module provides functions for extracting and transforming datetime values from a Fuseki database. It includes methods to connect to the database, retrieve the latest update datetime, and handle datetime transformations.

## Features

- **Latest Update Extraction**: Retrieves the most recent update datetime from the Fuseki database.
- **Datetime Transformation**: Converts datetime strings from the Fuseki database to a standardized format.
- **Error Handling**: Provides error handling for connection failures and missing datetime values.

## Usage

To use the functions in `fuseki_date_extraction.py`, you need to provide the necessary authentication credentials and connection details for the Fuseki database. Then, you can call the functions to extract and transform datetime values as needed.

### Latest Update Extraction

The `get_latest_fuseki_update` function connects to the Fuseki database and retrieves the latest update datetime. If the database is empty, it returns a placeholder datetime value.

### Datetime Transformation

The `transform_datetime` function converts datetime strings from the Fuseki database to a standardized format. It removes timezone information and adds one second to the datetime value.

## Example Usage

```python
from tools.fuseki_date_extraction import get_latest_fuseki_update

# Initialize Fuseki client and query
fuseki_client = FusekiClient(...)
latest_update_fuseki_query = QUERY_LATEST_LOCATIE_DATE

# Get the latest update datetime from the Fuseki database
latest_date = get_latest_fuseki_update(fuseki_client, latest_update_fuseki_query)
print(f"Latest update datetime: {latest_date}")
```

## Dependencies

- `datetime`: Standard library module for working with datetime values.
- `logging`: Standard library module for logging messages.
- `tools`: Custom tools module for error handling and printing.
- `httpx`: External library for making HTTP requests.
- `printer`: Custom module for printing messages.
- `handle_errors`: Custom module for handling errors.

# RDF Utilities

The `rdf_utils.py` module provides the function for generating RDF graphs using morph-kgc mapping engine.

## Features

- **RDF Graph Generation**: Generates an RDF graph from a configuration file using the `morph_kgc` library.

## Usage

To use the functions in `rdf_utils.py`, you need to provide input files or configuration details as required. Then, you can call the functions to perform the desired RDF-related operations.

### RDF Graph Generation

The `generate_rdf_graph` function generates an RDF graph based on the provided configuration file path. It utilizes the `morph_kgc` library for materializing the RDF graph.

## Example Usage

```python
from tools.rdf_utils import generate_rdf_graph

# Generate RDF graph
config_ini_path = "config.ini"
rdf_graph = generate_rdf_graph(config_ini_path)
print("RDF graph generated successfully.")
```

## Dependencies

- `logging`: Standard library module for logging messages.
- `morph_kgc`: External library for generating RDF graphs.

# CSV Utilities

The `csv_utils.py` module provides functions for working with the demo input CSV file, including comparing timestamps in a CSV file with a given latest date. This is used to introduce a break condition in the transformation code

## Features

- **Compare Timestamps with Latest Date**: Compares timestamps in a CSV file with a provided latest date and stops execution if the timestamp is less than or equal to the latest date.

## Usage

You can use the `compare_input_with_latest_date` function to compare timestamps in a CSV file with a given latest date. This function reads the CSV file located at the specified path and compares the `location_modified` timestamps with the latest date. If any timestamp is less than or equal to the latest date, the function stops execution.

## Example Usage

```python
from tools.csv_utils import compare_input_with_latest_date

# Specify the path to the CSV file and the latest date
output_csv_path = "output.csv"
latest_date = "2024-03-05T17:52:18+00:00"

# Compare timestamps with the latest date
compare_input_with_latest_date(output_csv_path, latest_date)
```

## Dependencies

- `csv`: Standard library module for reading and writing CSV files.
- `sys`: Standard library module for system-specific parameters and functions.
- `datetime`: Standard library module for manipulating dates and times.
- `timezone`: Standard library module for dealing with timezones.