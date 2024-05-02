import pathlib

TRANSFORMER_ROOT = str(pathlib.Path().absolute())

# variables for input and output data
# the type of entity, this is a variable used when working with multiple entities/yarrrml files in transformation code
LOCATIE_TYPE = "locatie"
ACTIVITEIT_TYPE = "activiteit"
DEELNAME_TYPE = "deelname"
PARTICIPANT_TYPE = "participant"
ORGANISATOR_TYPE = "organisator"
UITVOERDER_TYPE = "uitvoerder"

# the output port name as declared in the data-product.yml used to store rdf data in fuseki
FUSEKI_OUTPUT_PORT_NAME = "demosparql"

