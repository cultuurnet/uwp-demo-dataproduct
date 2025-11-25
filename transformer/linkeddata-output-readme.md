# Exploring Linked Data Output

This document explains how to explore and query the RDF (Resource Description Framework) data that your transformation pipeline has loaded into Fuseki, a SPARQL server for storing and querying linked data.

## What is Fuseki?

[Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) is a SPARQL server that provides a REST API for storing and querying RDF data. In the data mesh architecture, Fuseki serves as the **output port** for your dataproduct, making your transformed linked data accessible via SPARQL queries.

### Key Concepts

- **Dataset**: A Fuseki dataset is a container that holds one or more RDF graphs. Each dataproduct has its own dataset.
- **Named Graph**: A named graph is an RDF graph identified by a URI. In this dataproduct, each entity type (e.g., `locatie`, `activiteit`, `participant`) is stored in its own named graph for isolation and easier management.
- **Default Graph**: The default graph is a special graph that can be queried without specifying a graph name. Some datasets use it, while others rely solely on named graphs.
- **SPARQL**: SPARQL (SPARQL Protocol and RDF Query Language) is the standard query language for RDF data, similar to SQL for relational databases.

## Accessing Your Data

### Local Development Environment

When running the dataproduct locally using the Data Product CLI, the output data is available at:

- **Endpoint**: `http://localhost:3030`
- **Dataset**: `domain.dataProductName.outputPortName`
- **Authentication**: When redirected to the OpenID login page, you can use any username (authentication is typically disabled in local development)

### Production Environment

In production, the Fuseki endpoint URL and authentication details are configured through environment variables set by the platform. The dataset name follows the same pattern: `domain.dataProductName.outputPortName`.

## SPARQL Query Endpoints

Fuseki provides several endpoints for different operations:

- **Query endpoint**: `/domain.dataProductName.outputPortName/query` - Execute SELECT, CONSTRUCT, ASK, and DESCRIBE queries
- **Update endpoint**: `/domain.dataProductName.outputPortName/update` - Execute INSERT, DELETE, and other update operations
- **Data endpoint**: `/domain.dataProductName.outputPortName/data` - Direct access to graph data

## SPARQL Queries

### Exposing the Full Vocabulary of a Graph

When exploring a new dataset, it's helpful to understand what types of entities and properties are present. This query returns all predicates (properties) and their types for subjects that have an explicit type declaration.

**Use case**: Understanding the structure of your data, discovering available properties, and identifying which predicates link to resources vs. literals.

**Graph pattern**: Return all predicates and objects for subjects that are a 'type':
- If the object is of type IRI, bind "Resource predicate" to the pType variable
- If not, bind "Literal predicate" to the pType variable

```sparql
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

**What this query does**:
- Finds all subjects (`?s`) that have a type (`a ?t`)
- For each subject, finds all predicates (`?p`) and objects (`?o`)
- Categorizes predicates as either "Resource Predicate" (links to other resources) or "Literal Predicate" (contains data values)
- Groups and orders results by type and predicate for easy reading

### Constructing the Graph Schema

A more general CONSTRUCT query can be created to surface the graph schema (ontology) as a sub-graph. This is particularly useful when you don't have explicit schema documentation.

**Use case**: 
- Discovering the implicit schema/ontology of your data
- Planning vocabulary improvements and refactoring
- Understanding relationships between different entity types
- Creating documentation from the actual data structure

**Why this is useful**: This query works in any situation and does not require explicit RDFS classes, RDF properties, or explicit domains and ranges to be present. Instead, it constructs the graph schema efficiently for any graph by analyzing the actual data patterns.

```sparql
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

**What this query does**:
- For each subject with a type (`?domain`), finds all predicates (`?p`) and their objects (`?o`)
- If the object is a resource (has a type `?ot`), uses that type as the range
- If the object is a literal, uses its datatype as the range
- Constructs a schema graph showing domain-predicate-range relationships

**Using the result**: You can save the CONSTRUCT result as RDF and use it to understand your data structure, or visualize it using tools like [rdf-grapher](https://www.ldf.fi/service/rdf-grapher).

### Listing All Named Graphs

Each entity type in this dataproduct is stored in its own named graph. This query returns a list of all graph URIs in the dataset.

**Use case**: 
- Discovering which entity types have been loaded
- Identifying specific graphs to query or manage
- Understanding the organization of your data

```sparql
SELECT DISTINCT ?g
WHERE {
  GRAPH ?g {
    ?s ?p ?o
  }
}
```

**What this query does**:
- Finds all named graphs (`?g`) that contain at least one triple
- Returns the unique graph URIs

**Example output**: You might see graphs like:
- `<https://data.cultuurparticipatie.be/graph/locatie>`
- `<https://data.cultuurparticipatie.be/graph/activiteit>`
- `<https://data.cultuurparticipatie.be/graph/participant>`

### Describing a Specific Graph

This query constructs a unified graph containing all triples from one or more named graphs. It's useful for extracting and visualizing a complete entity type's data.

**Use case**:
- Extracting all data for a specific entity type
- Visualizing relationships within a graph
- Exporting data for analysis or transformation
- Debugging data quality issues

```sparql
CONSTRUCT {
  ?s ?p ?o
}
WHERE {
  GRAPH ?g {
    ?s ?p ?o
  }
}
```

**Visualizing the result**: The resulting n-triples can be visualized as a connected graph using online tools like [rdf-grapher](https://www.ldf.fi/service/rdf-grapher):

1. Copy the n-triples from the query response
2. Paste them as RDF data in the input field
3. Specify **From format** as N-Triples
4. Specify **To format** (e.g., Turtle for readability)
5. Send form as HTTP POST
6. Visualize the graph structure

**Tip**: To query a specific named graph, add a filter:
```sparql
CONSTRUCT {
  ?s ?p ?o
}
WHERE {
  GRAPH <https://data.cultuurparticipatie.be/graph/locatie> {
    ?s ?p ?o
  }
}
```

## SPARQL UPDATE Operations

SPARQL UPDATE queries allow you to modify the data in Fuseki. **Important**: Change the endpoint from `/query` to `/update` to perform UPDATE operations.

**Update endpoint**: `/domain.dataProductName.outputPortName/update`

### Deleting a Specific Named Graph

Manually delete a created graph to rerun the transformation code for that entity type. This is useful during development when you want to reprocess data without affecting other entity types.

**Use case**:
- Reprocessing a specific entity type after fixing transformation logic
- Removing test data
- Cleaning up incorrectly loaded data

```sparql
DROP GRAPH <graph_uri>
```

**Example**:
```sparql
DROP GRAPH <https://data.cultuurparticipatie.be/graph/locatie>
```

**Note**: After dropping a graph, you can rerun your transformation pipeline, and it will detect that no data exists for that entity type and process all available input data.

### Deleting All Data

Clear all graphs and triples in the Fuseki dataset. **Use with caution**: This removes all data from the dataset.

**Use case**:
- Starting fresh during development
- Clearing test data
- Resetting the dataset for a complete reprocessing

```sparql
DROP ALL
```

**Warning**: This operation cannot be undone. Make sure you have backups or can regenerate the data before executing this query.

## Best Practices

1. **Use named graphs**: Store different entity types in separate named graphs for better organization and easier management.

2. **Query specific graphs**: When possible, query specific named graphs rather than the union graph for better performance:
   ```sparql
   SELECT ?s ?p ?o
   WHERE {
     GRAPH <https://data.cultuurparticipatie.be/graph/locatie> {
       ?s ?p ?o
     }
   }
   ```

3. **Limit result sets**: When exploring large datasets, use `LIMIT` to avoid overwhelming results:
   ```sparql
   SELECT ?s ?p ?o
   WHERE { ?s ?p ?o }
   LIMIT 100
   ```

4. **Use CONSTRUCT for schema discovery**: The CONSTRUCT queries shown above are powerful tools for understanding your data structure without requiring explicit schema documentation.

5. **Test queries locally**: Always test your SPARQL queries in the local development environment before using them in production scripts or applications.

## Additional Resources

- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [SPARQL 1.1 Update](https://www.w3.org/TR/sparql11-update/)
- [Apache Jena Fuseki Documentation](https://jena.apache.org/documentation/fuseki2/)
- [RDF Grapher - Visualize RDF Graphs](https://www.ldf.fi/service/rdf-grapher)
