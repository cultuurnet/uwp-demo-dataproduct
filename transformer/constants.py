import pathlib

TRANSFORMER_ROOT = str(pathlib.Path().absolute())

# variables for input and output data
# the type of entity, this is a variable used when working with multiple entities/yarrrml files in transformation code
LOCATIE_TYPE = "locatie"
ACTIVITEIT_TYPE = "activiteit"
DEELNAME_TYPE = "deelname"
PARTICIPANT_TYPE = "participant"
# the location of the yarrrml file created and maintained by the data product developer
LOCATIE_YARRRML_PATH = TRANSFORMER_ROOT + "/yarrrml-data/locatie_yarrrml.yml"
ACTIVITEIT_YARRRML_PATH = TRANSFORMER_ROOT + "/yarrrml-data/activiteit_yarrrml.yml"
DEELNAME_YARRRML_PATH = TRANSFORMER_ROOT + "/yarrrml-data/deelname_yarrrml.yml"
PARTICIPANT_YARRRML_PATH = TRANSFORMER_ROOT + "/yarrrml-data/participant_yarrrml.yml"
# the location of the automatically generated RML file by the transform_yarrrml_to_rml function
LOCATIE_OUTPUT_RML_PATH = TRANSFORMER_ROOT + "/temp/rml-data/locatie_rml.ttl"
ACTIVITEIT_OUTPUT_RML_PATH = TRANSFORMER_ROOT + "/temp/rml-data/activiteit_rml.ttl"
DEELNAME_OUTPUT_RML_PATH = TRANSFORMER_ROOT + "/temp/rml-data/deelname_rml.ttl"
PARTICIPANT_OUTPUT_RML_PATH = TRANSFORMER_ROOT + "/temp/rml-data/participant_rml.ttl"
# the output port name as declared in the data-product.yml used to store rdf data in fuseki
FUSEKI_OUTPUT_PORT_NAME = "demosparql"

