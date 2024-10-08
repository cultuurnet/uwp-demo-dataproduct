from datetime import datetime, timedelta
import logging
from tools.tools import handle_errors, printer


QUERY_LATEST_LOCATIE_DATE = """
    PREFIX dcterms: <http://purl.org/dc/terms/>

    SELECT (MAX(?modified) AS ?mostRecentModifiedDate) WHERE {
        GRAPH ?g {
        ?s a dcterms:Location ;
           dcterms:modified ?modified .
        }
    }
"""

QUERY_LATEST_ACTIVITEIT_DATE = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>

    SELECT (MAX(?modified) AS ?mostRecentModifiedDate) WHERE {
        GRAPH ?g {
        ?s a cidoc:E7_Activity ;
           dcterms:modified ?modified .
        }
    }
"""

QUERY_LATEST_PARTICIPANT_DATE = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX cp: <https://data.vlaanderen.be/ns/cultuurparticipatie#>

    SELECT (MAX(?modified) AS ?mostRecentModifiedDate) WHERE {
        GRAPH ?g {
        ?s a cp:Participant ;
           dcterms:modified ?modified .
        }
    }
"""

QUERY_LATEST_DEELNAME_DATE = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX cp: <https://data.vlaanderen.be/ns/cultuurparticipatie#>
    PREFIX m8g: <http://data.europa.eu/m8g/>

    SELECT (MAX(?modified) AS ?mostRecentModifiedDate) WHERE {
        GRAPH ?g {
        ?s a cp:Deelname ;
           cp:Deelname.tijdstip ?period .
        ?period m8g:startTime ?modified .
        }
    }
"""

QUERY_LATEST_ORGANISATOR_DATE = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX cp: <https://data.vlaanderen.be/ns/cultuurparticipatie#>
    PREFIX m8g: <http://data.europa.eu/m8g/>

    SELECT (MAX(?modified) AS ?mostRecentModifiedDate) WHERE {
        GRAPH ?g {
        ?s a cp:Organisator ;
           dcterms:modified ?modified .
        }
    }
"""

QUERY_LATEST_UITVOERDER_DATE = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX cp: <https://data.vlaanderen.be/ns/cultuurparticipatie#>
    PREFIX m8g: <http://data.europa.eu/m8g/>

    SELECT (MAX(?modified) AS ?mostRecentModifiedDate) WHERE {
        GRAPH ?g {
        ?s a cp:Uitvoerder ;
           dcterms:modified ?modified .
        }
    }
"""

@handle_errors
@printer
def get_latest_fuseki_update(FusekiClient, query: str, data_type) -> str:
    """
    Connects to a Fuseki database and retrieves the latest update datetime.
    If the database is empty, then return: 1990-01-01T00:00:00+02:00.
    """
    raw_most_recent_date = extract_most_recent_date(FusekiClient, query)
    most_recent_date = transform_datetime(raw_most_recent_date)
    logging.info(f"Most recent date in Fuseki store for {data_type}: {most_recent_date}")
    return most_recent_date


def extract_most_recent_date(FusekiClient, query: str) -> str:
    """
    Extract the latest datetime from the Fuseki store.
    """
    result_set = FusekiClient.query(query)
    if result_set["results"]["bindings"]:
        # Extract the datetime if it exists
        fuseki_datetime = extract_datetime(result_set)
        return fuseki_datetime
    else:
        # Return the placeholder date if no modified date is found
        return "1990-01-01T00:00:00.000+00:00"


def transform_datetime(fuseki_datetime: str) -> datetime:
    """
    Ensure the Fuseki datetime string is converted to a timezone-aware datetime object.
    Example input: "2018-09-25T11:56:56+00:00"
    """
    # If the timezone is 'Z' (UTC), replace it with '+00:00'
    if fuseki_datetime.endswith('Z'):
        fuseki_datetime = fuseki_datetime[:-1] + '+00:00'
    
    # Convert string to timezone-aware datetime object
    date = datetime.fromisoformat(fuseki_datetime)
    
    # Add one second to account for the adjustment
    date = date + timedelta(seconds=1)
    
    # Return the datetime object (with timezone)
    return date


def extract_datetime(result_set: dict) -> str:
    """
    Extract the datetime from the SPARQL result set.
    """
    bindings = result_set["results"]["bindings"]
    if bindings:
        # Extract the datetime if it exists
        most_recent_date = (
            bindings[0].get("mostRecentModifiedDate", {}).get("value", "")
        )
        if most_recent_date:
            return most_recent_date
    # Return the placeholder date if no modified date is found
    return "1990-01-01T00:00:00+01:00"
