# Table of Contents
- [Main Script](#main-script)
	- [Features](#features)
	- [Transformation Pipeline Pattern](#transformation-pipeline-pattern)
	- [Usage](#usage)
	- [Example Usage](#example-usage)
	- [Configuration](#configuration)
	- [Logging](#logging)
	- [Dependencies](#dependencies)
- [Python Version Check](#python-version-check)
	- [Features](#features-python)
	- [Usage](#usage-python)
	- [Dependencies](#dependencies-python)
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
		- [SHACL Validation](#shacl-validation)
	- [Example Usage](#example-usage-3)
	- [Dependencies](#dependencies-3)
- [CSV Utilities](#csv-utilities)
	- [Features](#features-4)
	- [Usage](#usage-4)
	- [Example Usage](#example-usage-4)
	- [Dependencies](#dependencies-4)

  
# Main Script

The `main.py` script orchestrates the process of transforming CSV data to RDF and loading it into Fuseki. It demonstrates the standard transformation pipeline pattern used across data products in the platform.

## Features

- **Python Version Validation**: Checks Python version compatibility with Paketo buildpack before processing
- **Data-Driven Configuration**: Entity types configured in `ENTITY_CONFIGURATIONS` list for easy extension
- **Incremental Updates**: Only processes new/changed data by comparing timestamps
- **Multi-CSV Support**: Handles YARRRML mappings that reference multiple CSV files
- **SHACL Validation**: Validates RDF data against SHACL shapes before loading
- **Structured Logging**: Comprehensive logging with timestamps and progress tracking
- **Error Handling**: Graceful error handling with clear error messages
- **Resource Management**: Proper cleanup of Fuseki client connections

## Transformation Pipeline Pattern

The script follows a standardized transformation pipeline pattern:

1. **Python Version Check**: Validates Python version compatibility with buildpack (prevents build failures)
2. **For each entity type**:
   - **Get Latest Modification Date**: Retrieves the latest modified date from Fuseki using `get_latest_fuseki_update`
   - **Check for New Data**: Compares input CSV timestamps with Fuseki date to determine if processing is needed
   - **Generate RDF Graph**: Creates RDF graph (N-Quads) from CSV using YARRRML mappings via `generate_conjunctive_graph`
   - **Validate RDF**: Validates generated RDF against SHACL shapes using `validate_per_graph`
   - **Clear Existing Graphs**: Removes existing named graphs for the entity type
   - **Load RDF Graph**: Loads the validated RDF graph into Fuseki

This pattern ensures:
- **Incremental updates**: Only processes new/changed data, improving efficiency
- **Data quality**: SHACL validation prevents invalid data from being loaded
- **Graph isolation**: Each entity type has its own named graph

> **Note on SHACL Validation**: SHACL validation is useful during development to catch data quality issues early. However, it can significantly slow down transformation runs in production. Consider disabling SHACL validation in production environments if performance is critical, or use it selectively for specific entity types.

## Usage

1. Ensure all required dependencies are installed (see `requirements.txt`)
2. Configure entity types in `ENTITY_CONFIGURATIONS` if needed
3. Ensure input CSV files are in `input-data/` directory
4. Ensure YARRRML mapping files are in `yarrrml-data/` directory
5. Ensure SHACL validation file is in `shacl-data/` directory
6. Run the script

## Example Usage

Run the main.py script using the CLI tool:
```bash
dp run
```

Or run directly:
```bash
python transformer/main.py
```

## Configuration

### Entity Types Configuration

Entity types are configured in the `ENTITY_CONFIGURATIONS` list, making it easy to add or remove entity types:

```python
ENTITY_CONFIGURATIONS = [
    (LOCATIE_TYPE, QUERY_LATEST_LOCATIE_DATE),
    (ACTIVITEIT_TYPE, QUERY_LATEST_ACTIVITEIT_DATE),
    (DEELNAME_TYPE, QUERY_LATEST_DEELNAME_DATE),
    # Add more entity types here
]
```

### Path Configuration

Paths are automatically resolved relative to the transformer directory:
- `input-data/`: Input CSV files
- `yarrrml-data/`: YARRRML mapping files
- `shacl-data/`: SHACL validation files

### Multi-CSV YARRRML Mappings

When YARRRML mappings reference multiple CSV files (e.g., `activiteit_results.csv`, `activiteit_prijsinfo_mapping.csv`), the script handles them automatically. The YARRRML file specifies the paths, and morph-kgc resolves them correctly.

**Important**: Do not set `file_path` in the morph-kgc config when using multi-CSV mappings, as it would override all source paths.

## Logging

The script uses structured logging with timestamps:

- **Format**: `YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message`
- **Entity Type Prefixes**: All entity-specific logs are prefixed with `[ENTITY_TYPE]`
- **Progress Indicators**: Shows step progress (e.g., `Step 1/4`, `Step 2/4`)
- **Visual Indicators**: Uses `✓` for success and `✗` for failures
- **Summary**: Provides summary statistics at the end

Example log output:
```
2025-11-24 14:50:33 - __main__ - INFO - [ACTIVITEIT] Starting processing
2025-11-24 14:50:33 - __main__ - INFO - [ACTIVITEIT] Step 1/4: Generating RDF graph from CSV...
2025-11-24 14:50:33 - __main__ - INFO - [ACTIVITEIT] ✓ Generated 1,234 triples
```

## Dependencies

- `logging`: Standard library module for logging (with timestamp formatting)
- `pathlib.Path`: Standard library for path handling
- `rdflib.Graph`: RDF graph manipulation
- `FusekiClient`: Custom client class for interacting with Fuseki server
- `get_latest_fuseki_update`: Function for retrieving latest modified date from Fuseki
- `generate_conjunctive_graph`: Function for generating RDF graph from CSV using YARRRML
- `validate_per_graph`: Function for SHACL validation
- `compare_input_date_with_latest_date`: Function for comparing CSV timestamps with Fuseki date
- `check_python_version`: Function for Python version buildpack validation
- `constants`: Module containing constant values (entity types, port names)

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

# Python Version Check

The `python_version_check.py` module validates that the Python version specified in `.python-version` is supported by the Paketo buildpack before processing begins.

## Features

- **Buildpack Compatibility Check**: Queries Paketo buildpack to verify Python version support
- **Early Failure Detection**: Catches version incompatibilities before build/deployment
- **Caching**: Caches supported versions to reduce API calls
- **Clear Warnings**: Provides actionable error messages with fix instructions

## Usage

The check runs automatically at the start of `main.py` before any transformation code executes. It reads the Python version from `.python-version` and validates it against supported versions from the Paketo buildpack.

If the version is not supported, a warning is logged with:
- The specified version
- List of supported versions
- Instructions to fix (delete venv, update .python-version)

## Dependencies

- `urllib`: Standard library for HTTP requests
- `json`: Standard library for JSON parsing
- `pathlib`: Standard library for path handling
- `logging`: Standard library for logging

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

The `rdf_utils.py` module provides functions for generating RDF graphs using the morph-kgc mapping engine and validating them against SHACL shapes.

## Features

- **RDF Graph Generation**: Generates a conjunctive RDF graph (N-Quads) from CSV data using YARRRML mappings
- **SHACL Validation**: Validates RDF graphs against SHACL shapes on a per-graph basis
- **Memory Management**: Includes memory profiling capabilities

## Usage

To use the functions in `rdf_utils.py`, you need to provide a morph-kgc configuration string (INI format) that specifies the YARRRML mapping file. The function will generate an RDF graph from the CSV data.

### RDF Graph Generation

The `generate_conjunctive_graph` function generates a conjunctive RDF graph (N-Quads format) based on the provided configuration string. It utilizes the `morph_kgc` library for materializing the RDF graph.

**Configuration Format**:
```ini
[CONFIGURATION]
output_format=N-QUADS

[DataSource1]
mappings=yarrrml-data/entity_yarrrml.yml
```

**Important**: When YARRRML mappings reference multiple CSV files, do not set `file_path` in the config, as it would override all source paths specified in the YARRRML file.

### SHACL Validation

The `validate_per_graph` function validates each named graph in a conjunctive graph against SHACL shapes. This provides faster validation than validating the entire graph at once.

> **Performance Note**: SHACL validation can be useful during development to catch data quality issues early. However, it can significantly slow down transformation runs in production, especially for large datasets. Consider disabling SHACL validation in production environments if performance is critical, or use it selectively for specific entity types during development and testing phases.

## Example Usage

```python
from tools.rdf_utils import generate_conjunctive_graph, validate_per_graph
from rdflib import Graph

# Build morph-kgc configuration
config_ini = """[CONFIGURATION]
output_format=N-QUADS

[DataSource1]
mappings=yarrrml-data/activiteit_yarrrml.yml
"""

# Generate RDF graph
graph_store = generate_conjunctive_graph(config_ini)
print(f"Generated {len(graph_store)} triples")

# Load SHACL shapes
shacl_graph = Graph()
shacl_graph.parse("shacl-data/cultuurparticipatie_shacl.ttl", format="turtle")

# Validate
is_valid, _, failure_reason = validate_per_graph(graph_store, shacl_graph)
if is_valid:
    print("SHACL validation passed")
else:
    print(f"SHACL validation failed: {failure_reason}")
```

## Dependencies

- `logging`: Standard library module for logging messages
- `morph_kgc`: External library for generating RDF graphs from YARRRML mappings
- `rdflib.ConjunctiveGraph`: For handling N-Quads format
- `pyshacl`: For SHACL validation
- `memory_profiler`: For memory profiling (optional)

# CSV Utilities

The `csv_utils.py` module provides functions for comparing timestamps in CSV files with the latest date stored in Fuseki. This is used to determine if new data needs to be processed (incremental update pattern).

## Features

- **Timestamp Comparison**: Compares modification timestamps in CSV files with the latest date in Fuseki
- **Incremental Processing**: Returns `True` if all data is already processed (stop condition), `False` if new data exists
- **Entity Type Support**: Works with any entity type by using dynamic column names

## Usage

The `compare_input_date_with_latest_date` function reads a CSV file and checks if any rows have modification dates newer than the latest date in Fuseki. This determines whether processing should continue or stop.

**Function Behavior**:
- Returns `True` if all timestamps in CSV are <= latest_date (all data already processed - stop condition)
- Returns `False` if any timestamp in CSV is > latest_date (new data exists - continue processing)

**Column Naming Convention**:
The function expects a column named `{data_type}_modifieddate` (e.g., `locatie_modifieddate`, `activiteit_modifieddate`).

## Example Usage

```python
from tools.csv_utils import compare_input_date_with_latest_date
from datetime import datetime

# Specify the path to the CSV file, latest date, and entity type
csv_path = "input-data/activiteit_results.csv"
latest_date = datetime.fromisoformat("2024-03-05T17:52:18+00:00")
data_type = "activiteit"

# Check if new data exists
all_processed = compare_input_date_with_latest_date(csv_path, latest_date, data_type)

if all_processed:
    print("All data already processed")
else:
    print("New data found, processing...")
```

## Dependencies

- `csv`: Standard library module for reading CSV files
- `datetime`: Standard library module for manipulating dates and times