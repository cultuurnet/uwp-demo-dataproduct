import logging
import morph_kgc
from memory_profiler import profile
import gc
from pyshacl import validate

from rdflib import ConjunctiveGraph

# oxigraph directly handles quads (=includes the graph the triple is in)
# ! using oxigraph might create a memory leak !
def generate_rdf_oxigraph(config_ini_path):
    g = morph_kgc.materialize_oxigraph(config_ini_path)
    logging.info("RDF oxigraph generated successfully.")

    gc.collect()

    return g


def generate_conjunctive_graph(config_ini_path):
    g = materialize_conjunctive_graph(config_ini_path)
    logging.info("RDF graph generated successfully.")
    
    return g

@profile
def materialize_conjunctive_graph(config, python_source=None):
    triples = morph_kgc.materialize_set(config, python_source)

    graph = ConjunctiveGraph()
    if triples:
        rdf_ntriples = '.\n'.join(triples) + '.'
        graph.parse(data=rdf_ntriples, format='nquads')
    return graph


# validate on a per-graph basis, which can be quicker than validating all graphs together
def validate_per_graph(graph, shacl_graph):
    for g in graph.contexts():
        print(f"Validating graph context: {g.serialize(format='turtle')}")
        (is_valid, failure, failure_reason) = validate(g, shacl_graph)
        if not is_valid:
            print(f"Failure reason: {failure_reason}")
            return (is_valid, failure, failure_reason)
        
    return (is_valid, failure, failure_reason)