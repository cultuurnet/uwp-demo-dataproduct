from os import environ
import httpx
from authlib.integrations.httpx_client import OAuth2Client
from authlib.integrations.base_client.errors import InvalidTokenError
import logging

from pyoxigraph import Store
from tools.tools import OUTPUT_PORTS, timer
from rdflib import ConjunctiveGraph, Dataset
from functools import wraps
from memory_profiler import profile

SCOPE = 'profile email openid'

def exception_handler(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except httpx.HTTPStatusError as e:
            logging.error(
                f"Failed to connect to Fuseki: {e.response.status_code} {e.response.text}"
            )
            raise e
        except InvalidTokenError:
            logging.error(
                    "Invalid token encountered. Refreshing token and retrying..."
                )
            self.refresh_token()
            return func(self, *args, **kwargs)
    return wrapper

def get_oauth_client(client_id: str, client_secret: str, token_endpoint: str) -> OAuth2Client:
    """
    Return configured OAuth2Client.
    """
    client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        scope= SCOPE,
        token_endpoint=token_endpoint
    )
    # Using httpx.AsyncClient() as the session manager
    client.session = httpx.Client()
    return client

def configure_oauth_security(token_url: str):
    if not token_url.startswith("https://"):
        environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# authentication function
def get_httpx_client(fuseki_output_port_name: str) -> OAuth2Client:
    """
    Returns an authenticated httpx client for the Fuseki server.
    """
    # Add OIDC security to the 'httpx' Python HTTP client
    token_url = OUTPUT_PORTS[fuseki_output_port_name]["AUTH_TOKEN_URL"]
    client_id = OUTPUT_PORTS[fuseki_output_port_name]["AUTH_CLIENT_ID"]
    client_secret = OUTPUT_PORTS[fuseki_output_port_name]["AUTH_CLIENT_SECRET"]
    client = get_oauth_client(client_id, client_secret, token_url)
    configure_oauth_security(token_url)
    client.fetch_token(token_url)
    return client

def get_fuseki_base_endpoint(fuseki_output_port_name: str) -> str:
    """
    Returns the url of the Fuseki server.
    """
    fuseki_url = OUTPUT_PORTS[fuseki_output_port_name]["URL"]
    fuseki_dataset = OUTPUT_PORTS[fuseki_output_port_name]["DATASET"]
    return f"{fuseki_url}/{fuseki_dataset}"

def refresh_token(self) -> OAuth2Client:
    return get_httpx_client(self.fuseki_output_port_name)

class FusekiClient:
    """
    Client for Fuseki server.
    """
    def __init__(self, output_port_name):
        self.fuseki_output_port_name = output_port_name
        self.base_endpoint = get_fuseki_base_endpoint(self.fuseki_output_port_name)
        self.refresh_token()

    def refresh_token(self):
        self.client = get_httpx_client(self.fuseki_output_port_name)

    @exception_handler
    def query(self, sparql_query: str):
        """
        Queries the Fuseki server with the given SPARQL query.
        Returns the response in JSON format.
        """
        query_endpoint = f"{self.base_endpoint}/query"
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = self.make_post_request(query_endpoint, headers, query=sparql_query)
        return response.json()


    @timer
    @exception_handler
    def write_graph(self, dataset: Dataset):
        """
        Writes the given dataset to the Fuseki server.
        """
        # Iterate through named graphs in the dataset
        for graph_uri, named_graph in dataset.graphs():
            # Prepare the write endpoint for each named graph
            write_endpoint = f"{self.base_endpoint}/data?graph={str(graph_uri)}"
            headers = {
                "Content-Type": "application/n-quads"
            }

            # Serialize the named graph to N-Quads
            data = named_graph.serialize(format='nquads').encode('utf-8')

            try:
                self.make_post_request(write_endpoint, headers, data=data)
            except InvalidTokenError:
                logging.error("Invalid token encountered. Refreshing token and retrying...")
                refresh_token(self)
                self.make_post_request(write_endpoint, headers, data=data)        


    def make_post_request(self, endpoint: str, headers: dict, data: bytes = None, query: str = "") -> httpx.Response:
        """
        Makes a post request to the given endpoint with the given data and headers.
        """
        if data:
            response = self.client.post(endpoint, content=data, headers=headers, timeout=None)
            logging.info("Successfully uploaded batch to Fuseki.")
        elif query:
            response = self.client.post(endpoint, data={'query': query}, headers=headers, timeout=None)
            logging.info("Successfully queried Fuseki.")
        else:
            # Handle the case when neither 'data' nor 'query' is provided
            raise ValueError("Either 'data' or 'query' must be provided.")

        response.raise_for_status()
        return response


    def clear_graphs(self, dataset):
        """
        Clears the graphs in the Fuseki server corresponding to the provided dataset.
        """
        try:
            if isinstance(dataset, ConjunctiveGraph):
                graph_uris = set([f"<{graph.identifier}>" for graph in dataset.contexts()])
            else:    
                graph_uris = dataset.named_graphs()
            
            drop_statements = "\n".join(f"CLEAR SILENT GRAPH {graph_uri};" for graph_uri in graph_uris)
            # Log or print the drop statements
            logging.debug(f"Drop statements:\n{drop_statements}")

            clear_endpoint = f"{self.base_endpoint}/update"
            headers = {
                "Content-Type": "application/sparql-update"
            }
            data = drop_statements.encode('utf-8')

            response = self.client.post(clear_endpoint, content=data, headers=headers)
            response.raise_for_status()

            logging.info(f"Cleared graphs in Fuseki. Status Code: {response.status_code}")

        except InvalidTokenError:
            logging.error("Invalid token encountered. Refreshing token and retrying...")
            self.client = refresh_token(self)
            self.clear_graphs(dataset)  # Retry after token refresh

    #@profile
    def load_store(self, graph: Store):
        """
        Loads the provided graph Store into the Fuseki server.
        """

        try:
            store_endpoint = f"{self.base_endpoint}/data"
            headers = {
                "Content-Type": "application/n-quads"
            }
            data = str(graph).encode('utf-8')

            response = self.client.post(store_endpoint, content=data, headers=headers)
            response.raise_for_status()

            logging.info(f"Stored graph Store in Fuseki. Status Code: {response.status_code}")

        except InvalidTokenError:
            logging.error("Invalid token encountered. Refreshing token and retrying...")
            refresh_token(self)
            self.load_store(graph)  # Retry after token refresh

    @timer
    @exception_handler
    def load_conjunctive_graph(self, graph: ConjunctiveGraph):
        """
        Writes the given dataset to the Fuseki server.
        """

        try:
            store_endpoint = f"{self.base_endpoint}/data"
            headers = {
                "Content-Type": "application/n-quads"
            }
            data = graph.serialize(format="nquads")

            response = self.client.post(store_endpoint, content=data, headers=headers)
            response.raise_for_status()

            logging.info(f"Stored graph Store in Fuseki. Status Code: {response.status_code}")

        except InvalidTokenError:
            logging.error("Invalid token encountered. Refreshing token and retrying...")
            refresh_token(self)
            self.load_conjunctive_graph(graph)  # Retry after token refresh

    @profile
    def close(self):
        """
        Closes the client to release resources.
        """
        self.client.close()
        logging.info("Closed FusekiClient.")
