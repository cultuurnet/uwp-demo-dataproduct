import logging
from fuseki_client import FusekiClient
from fuseki_date_extraction import (
    get_latest_fuseki_update,
    QUERY_LATEST_LOCATIE_DATE,
)
from rdf_utils import generate_rdf_graph, transform_yarrrml_to_rml
from csv_utils import compare_input_with_latest_date
from constants import (
    FUSEKI_OUTPUT_PORT_NAME,
    LOCATIE_OUTPUT_RML_PATH,
    LOCATIE_TYPE,
    LOCATIE_YARRRML_PATH,
)


# Set the logging level to INFO
# add `force=True` to also set logging level of libraries
logging.basicConfig(level=logging.INFO, force=True)


def push_data(data_type, latest_update_fuseki_query):
    fuseki_client = FusekiClient(FUSEKI_OUTPUT_PORT_NAME)
    output_csv_path = "input-data/locatie_results.csv"
    config_ini = f"""[CONFIGURATION]
                output_format=N-QUADS

                [DataSource1]
                mappings: output-data/{data_type}_rml.ttl
                file_path: {output_csv_path}
                """

    previous_latest_date = ""
    while True:
        # Step 1: Find the latest modified date, to only add newly modified/created entities
        latest_date = get_latest_fuseki_update(
            fuseki_client, latest_update_fuseki_query
        )

        # Check if input data has new entities to process
        compare_input_with_latest_date(output_csv_path, latest_date)

        # Step 3: Generate RDF graph (n-quads) from CSV (found in `file_path`) using morph-kgc
        graph_store = generate_rdf_graph(config_ini)

        # Step 4: Clear existing named entity graphs in Fuseki
        fuseki_client.clear_graphs(graph_store)

        # Step 5: Load the RDF graph (n-quads) into Fuseki
        fuseki_client.load_store(graph_store)


if __name__ == "__main__":
    transform_yarrrml_to_rml(LOCATIE_YARRRML_PATH, LOCATIE_OUTPUT_RML_PATH)
    push_data(LOCATIE_TYPE, QUERY_LATEST_LOCATIE_DATE)
