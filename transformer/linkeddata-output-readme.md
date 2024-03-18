# Local output location
The output data is available at the following locations:
- outputPortName: http://localhost:3030 in dataset "domain.dataProductName.outputPortName". Just use any username when redirected to the OpenID login page

# SPARQL Queries
## Expose the full vocabulary of a graph

Graph pattern: return all predicates and objects for subjects that are a 'type':
- if the object is of type IRI, bind "Resource predicate" to the pType variable
- if not, bind "Literal predicate" to the pType variable

```
SELECT DISTINCT ?t ?p ?pType
# search over default graph and all named graphs
FROM <urn:x-arq:UnionGraph>
WHERE {
    ?s ?p ?o ;
        a ?t .

    BIND (
    COALESCE(
        IF(isIRI(?o), "Resource Predicate", 1/0),
        "Literal Predicate"
        ) AS ?pType
    )
}
GROUP BY ?t ?p ?pType
ORDER BY ASC(?t) ASC(?p)
```

 ## Constructing the graph schema

A more general CONSTRUCT query can be created to surface the graph schema (ontology) as a sub-graph.

The query below will work in any situation and it does not require the explicit declaration of RDFS classes, RDF properties or explicit domains and ranges to be present. Instead, the query is able to construct the graph schema (i.e. ontology) efficiently for any graph.

This query can, for example, be used when you don't have a proper schema and want to see what's under-the-hood in terms of the graph vocabulary. This allows you to plan which structures to uplift, where to rationalise and which vocabulary structures to improve, consolidate or refactor.

```
CONSTRUCT {
    ?domain ?p ?range
}
# search over default graph and all named graphs
FROM <urn:x-arq:UnionGraph>
WHERE {
    ?s ?p ?o ;
        a ?domain .
    OPTIONAL {
        ?o a ?ot .
    }
    BIND(IF(BOUND(?ot), ?ot, DATATYPE(?o)) AS ?range)
}
```

## List all graphs
The following query returns a list of graph_uri values that can be used to dive deeper in the specific graph details or remove a specific graph (see below)

```
SELECT DISTINCT ?g
WHERE {
  GRAPH ?g {
    ?s ?p ?o
  }
}
```

## Describe a specific graph in n-triples
The following query constructs a new graph with all subjects, predicates and objects from the specified graph_uri in the WHERE clause.

It is interesting to visualize the resulting n-triples response as a graph, using an online tool like [rdf-grapher](https://www.ldf.fi/service/rdf-grapher) : 
1. copy the n-triples from the query response
2. paste them as RDF data in the input field
3. Specify From format as N-Triples
4. Specify To format
5. Visualize

```
CONSTRUCT {
  ?s ?p ?o
}
WHERE {
  GRAPH <graph_uri> {
    ?s ?p ?o
  }
}
```

# SPARQL UPDATE
Change the endpoint from `/query` to `/update` to perform SPARQL UPDATE queries:

```
/domain.dataProductName.outputPortName/update
```

## Delete a specific graph

Manually delete a created graph to rerun the transformation code for that entity

```
DROP GRAPH <graph_uri>
```