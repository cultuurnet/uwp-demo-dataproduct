"""
Data Product Transformation Pipeline

This script demonstrates the standard pattern for transforming CSV data to RDF
and loading it into Fuseki. It processes multiple entity types in sequence.

Transformation Pipeline Pattern:
1. Check Python version compatibility (buildpack validation)
2. For each entity type:
   a. Get latest modification date from Fuseki (incremental updates)
   b. Check if new data is available
   c. Generate RDF graph from CSV using YARRRML mappings
   d. Validate RDF against SHACL shapes
   e. Clear existing graphs in Fuseki
   f. Load new RDF graph into Fuseki

This pattern ensures:
- Incremental updates (only process new/changed data)
- Data quality (SHACL validation before loading)
- Graph isolation (each entity has its own named graph)
"""

import logging
from pathlib import Path
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
from tools.python_version_check import check_python_version

# Configure logging with timestamps and structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)
logger = logging.getLogger(__name__)

# Check Python version compatibility BEFORE any processing
check_python_version()

# Configuration: Entity types and their corresponding SPARQL queries
# This data-driven approach makes it easy to add/remove entity types
ENTITY_CONFIGURATIONS = [
    (LOCATIE_TYPE, QUERY_LATEST_LOCATIE_DATE),
    (ACTIVITEIT_TYPE, QUERY_LATEST_ACTIVITEIT_DATE),
   (DEELNAME_TYPE, QUERY_LATEST_DEELNAME_DATE),
   (PARTICIPANT_TYPE, QUERY_LATEST_PARTICIPANT_DATE),
   (ORGANISATOR_TYPE, QUERY_LATEST_ORGANISATOR_DATE),
   (UITVOERDER_TYPE, QUERY_LATEST_UITVOERDER_DATE),
]

# Paths configuration (relative to transformer directory)
TRANSFORMER_DIR = Path(__file__).parent
SHACL_FILE = TRANSFORMER_DIR / "shacl-data" / "cultuurparticipatie_shacl.ttl"
INPUT_DATA_DIR = TRANSFORMER_DIR / "input-data"
YARRRML_DATA_DIR = TRANSFORMER_DIR / "yarrrml-data"


def process_entity_type(
    data_type: str,
    latest_update_query: str,
    fuseki_client: FusekiClient,
    shacl_graph: Graph,
) -> bool:
    """
    Process a single entity type through the transformation pipeline.
    
    Args:
        data_type: Entity type identifier (e.g., "locatie", "participant")
        latest_update_query: SPARQL query to get latest modification date
        fuseki_client: Fuseki client instance
        shacl_graph: SHACL validation graph
        
    Returns:
        True if processing completed successfully, False otherwise
    """
    logger.info(f"[{data_type.upper()}] Starting processing")
    
    input_csv_path = INPUT_DATA_DIR / f"{data_type}_results.csv"
    yarrrml_file = YARRRML_DATA_DIR / f"{data_type}_yarrrml.yml"
    
    # Check if input files exist
    if not input_csv_path.exists():
        logger.warning(f"[{data_type.upper()}] Input CSV not found: {input_csv_path}. Skipping.")
        return False
    
    if not yarrrml_file.exists():
        logger.error(f"[{data_type.upper()}] YARRRML mapping not found: {yarrrml_file}. Cannot process.")
        return False
    
    logger.debug(f"[{data_type.upper()}] Input CSV: {input_csv_path}")
    logger.debug(f"[{data_type.upper()}] YARRRML mapping: {yarrrml_file}")
    
    # Build morph-kgc configuration
    # Note: Do NOT set file_path here when YARRRML mapping references multiple CSV files.
    # Setting file_path would override ALL source paths in the YARRRML with a single file.
    # The YARRRML mapping already specifies the correct paths relative to the transformer directory.
    config_ini = f"""[CONFIGURATION]
output_format=N-QUADS

[DataSource1]
mappings={yarrrml_file}
"""
    
    previous_latest_date = ""
    
    # Process data in batches (incremental updates)
    while True:
        # Step 1: Get latest modification date from Fuseki
        latest_date = get_latest_fuseki_update(fuseki_client, latest_update_query, data_type)
        logger.debug(f"[{data_type.upper()}] Latest date in Fuseki: {latest_date}")
        
        # Step 2: Check if new data is available
        # Note: compare_input_date_with_latest_date returns True if all data is already processed (stop condition)
        if compare_input_date_with_latest_date(str(input_csv_path), latest_date, data_type) or latest_date == previous_latest_date:
            logger.info(f"[{data_type.upper()}] No new data available. Processing complete.")
            break
        
        previous_latest_date = latest_date
        logger.info(f"[{data_type.upper()}] New data detected. Processing batch...")
        
        # Step 3: Generate RDF graph from CSV using YARRRML mappings
        logger.info(f"[{data_type.upper()}] Step 1/4: Generating RDF graph from CSV...")
        try:
            graph_store = generate_conjunctive_graph(config_ini)
            triple_count = len(graph_store)
            logger.info(f"[{data_type.upper()}] ✓ Generated {triple_count:,} triples")
        except Exception as e:
            logger.error(f"[{data_type.upper()}] ✗ Failed to generate RDF graph: {e}")
            return False
        
        # Step 4: Validate RDF against SHACL shapes
        logger.info(f"[{data_type.upper()}] Step 2/4: Validating RDF against SHACL shapes...")
        is_valid, _, failure_reason = validate_per_graph(graph_store, shacl_graph)
        
        if not is_valid:
            logger.error(f"[{data_type.upper()}] ✗ SHACL validation failed: {failure_reason}")
            logger.error(f"[{data_type.upper()}] Stopping processing to prevent invalid data from being loaded.")
            return False
        
        logger.info(f"[{data_type.upper()}] ✓ SHACL validation passed")
        
        # Step 5: Clear existing graphs for this entity type
        logger.info(f"[{data_type.upper()}] Step 3/4: Clearing existing graphs...")
        fuseki_client.clear_graphs(graph_store)
        logger.info(f"[{data_type.upper()}] ✓ Existing graphs cleared")
        
        # Step 6: Load new RDF graph into Fuseki
        logger.info(f"[{data_type.upper()}] Step 4/4: Loading graph into Fuseki...")
        try:
            fuseki_client.load_conjunctive_graph(graph_store)
            logger.info(f"[{data_type.upper()}] ✓ Successfully loaded {triple_count:,} triples into Fuseki")
        except Exception as e:
            logger.error(f"[{data_type.upper()}] ✗ Failed to load graph into Fuseki: {e}")
            return False
    
    return True


def main():
    """
    Main transformation pipeline.
    
    Processes all configured entity types in sequence.
    Each entity type follows the standard transformation pattern.
    """
    logger.info("=" * 80)
    logger.info("DATA PRODUCT TRANSFORMATION PIPELINE - STARTING")
    logger.info("=" * 80)
    
    # Load SHACL validation graph once (shared across all entity types)
    logger.info("Loading SHACL validation graph...")
    if not SHACL_FILE.exists():
        logger.error(f"✗ SHACL file not found: {SHACL_FILE}")
        return
    
    shacl_graph = Graph()
    try:
        shacl_graph.parse(str(SHACL_FILE), format="turtle")
        logger.info(f"✓ Loaded SHACL validation graph from {SHACL_FILE.name}")
    except Exception as e:
        logger.error(f"✗ Failed to load SHACL graph: {e}")
        return
    
    # Initialize Fuseki client (reused for all entity types)
    logger.info(f"Initializing Fuseki client for output port: {FUSEKI_OUTPUT_PORT_NAME}")
    fuseki_client = FusekiClient(FUSEKI_OUTPUT_PORT_NAME)
    logger.info("✓ Fuseki client initialized")
    
    # Process each entity type
    logger.info("")
    logger.info(f"Processing {len(ENTITY_CONFIGURATIONS)} entity type(s)...")
    logger.info("-" * 80)
    
    success_count = 0
    failed_types = []
    
    for idx, (data_type, latest_update_query) in enumerate(ENTITY_CONFIGURATIONS, 1):
        logger.info(f"\n[{idx}/{len(ENTITY_CONFIGURATIONS)}] Processing: {data_type}")
        logger.info("-" * 80)
        try:
            if process_entity_type(data_type, latest_update_query, fuseki_client, shacl_graph):
                success_count += 1
                logger.info(f"[{data_type.upper()}] ✓ Processing completed successfully")
            else:
                failed_types.append(data_type)
                logger.warning(f"[{data_type.upper()}] ✗ Processing failed")
        except Exception as e:
            failed_types.append(data_type)
            logger.error(f"[{data_type.upper()}] ✗ Unexpected error: {e}", exc_info=True)
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TRANSFORMATION PIPELINE SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total entity types: {len(ENTITY_CONFIGURATIONS)}")
    logger.info(f"Successfully processed: {success_count}")
    if failed_types:
        logger.warning(f"Failed: {len(failed_types)} - {', '.join(failed_types)}")
    logger.info("=" * 80)
    
    fuseki_client.close()
    logger.info("Fuseki client closed")


if __name__ == "__main__":
    main()
