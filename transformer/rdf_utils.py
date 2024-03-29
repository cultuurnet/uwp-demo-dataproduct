import os
import tempfile
import logging
import yatter
from ruamel.yaml import YAML
import morph_kgc

def transform_yarrrml_to_rml(input_yarrrml_path: str, data_type: str) -> str:
    """
    Transform a YARRRML file to an RML file using yatter library and store it in the system's temporary directory as 'location_rml.ttl'.

    Args:
        input_yarrrml_path (str): Path to the input YARRRML file.
        data_type (str): Name of the data type to be used in the filename.

    Returns:
        str: Path to the created RML file if conversion was successful, else an empty string.
    """
    yaml = YAML(typ="safe", pure=True)
    rml_content = yatter.translate(yaml.load(open(input_yarrrml_path)))
    if rml_content is None:
        logging.warning(f"Conversion of file to RML failed: {input_yarrrml_path}")
        return ""

    # Create a temporary file with specified name and .ttl extension to store the RML content
    temp_dir = tempfile.gettempdir()
    temp_rml_filename = f"{data_type}_rml.ttl"
    temp_rml_path = os.path.join(temp_dir, temp_rml_filename)
    with open(temp_rml_path, 'w') as temp_rml_file:
        temp_rml_file.write(rml_content)

    logging.info(f"RML file created and saved at: {temp_rml_path}")
    return temp_rml_path


def generate_rdf_graph(config_ini_path):
    g = morph_kgc.materialize_oxigraph(config_ini_path)
    logging.debug("RDF graph generated successfully.")
    return g
