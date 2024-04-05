import logging
import morph_kgc

def generate_rdf_graph(config_ini_path):
    g = morph_kgc.materialize_oxigraph(config_ini_path)
    logging.debug("RDF graph generated successfully.")
    return g
