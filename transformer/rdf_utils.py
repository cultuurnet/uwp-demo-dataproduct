import logging
import yatter
from ruamel.yaml import YAML
import morph_kgc


def transform_yarrrml_to_rml(input_yarrrml_path: str, output_rml_path: str) -> bool:
    """
    Transform a YARRRML file to an RML file using yatter library.

    Args:
        yarrrml_path (str): Path to the input YARRRML file.
        output_rml_path (str): Path to RML file that will be created.

    Returns:
        bool: true if conversion was successful
    """
    yaml = YAML(typ="safe", pure=True)
    rml_content = yatter.translate(yaml.load(open(input_yarrrml_path)))
    if rml_content is None:
        logging.warning(f"Conversion of file to RML failed: {input_yarrrml_path}")
        return False

    # Save the RML content to a file
    with open(output_rml_path, "w") as rml_file:
        rml_file.write(rml_content)

    # Log that the RML file is created and written to the specified path
    logging.info(f"RML file created and saved at: {output_rml_path}")
    return True


def generate_rdf_graph(config_ini_path):
    g = morph_kgc.materialize_oxigraph(config_ini_path)
    logging.debug("RDF graph generated successfully.")
    return g
