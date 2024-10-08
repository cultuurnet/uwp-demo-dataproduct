import logging

from rdflib import Graph

from tools.fuseki_client import FusekiClient
from tools.fuseki_date_extraction import (
    get_latest_fuseki_update,
    QUERY_LATEST_LOCATIE_DATE,
    QUERY_LATEST_ACTIVITEIT_DATE,
    QUERY_LATEST_PARTICIPANT_DATE,
    QUERY_LATEST_DEELNAME_DATE,
    QUERY_LATEST_ORGANISATOR_DATE,
    QUERY_LATEST_UITVOERDER_DATE,
)

from tools.rdf_utils import generate_conjunctive_graph, validate_per_graph
from tools.csv_utils import compare_input_date_with_latest_date
from tools.constants import (
    FUSEKI_OUTPUT_PORT_NAME,
    LOCATIE_TYPE,
    ACTIVITEIT_TYPE,
    DEELNAME_TYPE,
    PARTICIPANT_TYPE,
    ORGANISATOR_TYPE,
    UITVOERDER_TYPE,
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
                mappings=yarrrml-data/{data_type}_yarrrml.yml
                """

    previous_latest_date = ""
    
    shacl_graph = Graph()
    shacl_graph.parse("transformer/shacl-file/shacl-file.ttl", format="turtle")
    print(shacl_graph.serialize(format="turtle"))

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
        graph_store = generate_conjunctive_graph(config_ini)
        print(graph_store.serialize(format="nquads"))

        (is_valid, _, failure_reason) = validate_per_graph(graph_store, shacl_graph)
        if not is_valid:
            logging.warning(failure_reason)
            return

        # Step 4: Clear existing named entity graphs in Fuseki
        fuseki_client.clear_graphs(graph_store)

        # Step 5: Load the RDF graph (n-quads) into Fuseki
        fuseki_client.load_conjunctive_graph(graph_store)


if __name__ == "__main__":
    push_data(LOCATIE_TYPE, QUERY_LATEST_LOCATIE_DATE)
    push_data(ACTIVITEIT_TYPE, QUERY_LATEST_ACTIVITEIT_DATE)
    push_data(DEELNAME_TYPE, QUERY_LATEST_DEELNAME_DATE)
    push_data(PARTICIPANT_TYPE, QUERY_LATEST_PARTICIPANT_DATE)
    push_data(ORGANISATOR_TYPE, QUERY_LATEST_ORGANISATOR_DATE)
    push_data(UITVOERDER_TYPE, QUERY_LATEST_UITVOERDER_DATE)
