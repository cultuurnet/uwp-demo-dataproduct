import logging
from fuseki_client import FusekiClient
from fuseki_date_extraction import (
    get_latest_fuseki_update,
    QUERY_LATEST_LOCATIE_DATE,
    QUERY_LATEST_ACTIVITEIT_DATE,
    QUERY_LATEST_PARTICIPANT_DATE,
    QUERY_LATEST_DEELNAME_DATE,
)
from rdf_utils import generate_rdf_graph, transform_yarrrml_to_rml
from csv_utils import compare_input_date_with_latest_date
from constants import (
    FUSEKI_OUTPUT_PORT_NAME,
    LOCATIE_OUTPUT_RML_PATH,
    LOCATIE_TYPE,
    LOCATIE_YARRRML_PATH,
    ACTIVITEIT_OUTPUT_RML_PATH,
    ACTIVITEIT_TYPE,
    ACTIVITEIT_YARRRML_PATH,
    DEELNAME_OUTPUT_RML_PATH,
    DEELNAME_TYPE,
    DEELNAME_YARRRML_PATH,
    PARTICIPANT_OUTPUT_RML_PATH,
    PARTICIPANT_TYPE,
    PARTICIPANT_YARRRML_PATH,
)


# Set the logging level to INFO
# add `force=True` to also set logging level of libraries
logging.basicConfig(level=logging.INFO, force=True)


def push_data(data_type, latest_update_fuseki_query):
    fuseki_client = FusekiClient(FUSEKI_OUTPUT_PORT_NAME)
    input_csv_path = f"""input-data/{data_type}_results.csv"""
    config_ini = f"""[CONFIGURATION]
                output_format=N-QUADS

                [DataSource1]
                mappings=/tmp/{data_type}_rml.ttl
                """

    previous_latest_date = ""
    while True:
        # Step 1: Find the latest modified date, to only add newly modified/created entities
        latest_date = get_latest_fuseki_update(
            fuseki_client, latest_update_fuseki_query, data_type
        )

        # Step 2: Check if input data has new entities to process
        if compare_input_date_with_latest_date(input_csv_path, latest_date, data_type) or latest_date == previous_latest_date :
            # Stop condition met, move to the next data type
            break
        else:
            previous_latest_date = latest_date

        # Step 3: Generate RDF graph (n-quads) from CSV (found in `file_path`) using morph-kgc
        graph_store = generate_rdf_graph(config_ini)

        # Step 4: Clear existing named entity graphs in Fuseki
        fuseki_client.clear_graphs(graph_store)

        # Step 5: Load the RDF graph (n-quads) into Fuseki
        fuseki_client.load_store(graph_store)


if __name__ == "__main__":
    transform_yarrrml_to_rml(LOCATIE_YARRRML_PATH, LOCATIE_TYPE)
    transform_yarrrml_to_rml(ACTIVITEIT_YARRRML_PATH, ACTIVITEIT_TYPE)
    transform_yarrrml_to_rml(DEELNAME_YARRRML_PATH, DEELNAME_TYPE)
    transform_yarrrml_to_rml(PARTICIPANT_YARRRML_PATH, PARTICIPANT_TYPE)
    push_data(LOCATIE_TYPE, QUERY_LATEST_LOCATIE_DATE)
    push_data(ACTIVITEIT_TYPE, QUERY_LATEST_ACTIVITEIT_DATE)
    push_data(DEELNAME_TYPE, QUERY_LATEST_DEELNAME_DATE)
    push_data(PARTICIPANT_TYPE, QUERY_LATEST_PARTICIPANT_DATE)
