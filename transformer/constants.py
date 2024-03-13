import pathlib

TRANSFORMER_ROOT = str(pathlib.Path().absolute())

# variables for input and output data
# the location of the yarrrml file created and maintained by the data product developer
LOCATIE_YARRRML_PATH = TRANSFORMER_ROOT + "/input-data/locatie_yarrrml.yml"
# the location of the automatically generated RML file by the transform_yarrrml_to_rml function
LOCATIE_OUTPUT_RML_PATH = TRANSFORMER_ROOT + "/output-data/locatie_rml.ttl"
# the output port name as declared in the data-product.yml used to store rdf data in fuseki
FUSEKI_OUTPUT_PORT_NAME = "demosparql"
# the type of entity, this is a variable used when working with multiple entities/yarrrml files in transformation code
LOCATIE_TYPE = "locatie"
