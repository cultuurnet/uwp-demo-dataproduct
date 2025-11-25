# Demo Data Product

A reference implementation demonstrating best practices for building data products in the UiTwisselingsplatform (UWP) data mesh. This dataproduct serves as a learning resource and onboarding example for new data product developers.

## Overview

This demo dataproduct transforms CSV data into RDF (Resource Description Framework) linked data and publishes it to a Fuseki SPARQL endpoint. It demonstrates the standard transformation pipeline pattern used across data products in the platform, including:

- **Incremental data processing**: Only processes new or modified data based on timestamps
- **Multi-entity type support**: Processes multiple entity types (locations, activities, participants, etc.) in a data-driven configuration
- **Data quality validation**: Validates generated RDF against SHACL shapes before loading
- **Graph isolation**: Stores each entity type in its own named graph for better organization
- **Python version compatibility**: Validates Python version against Paketo buildpack requirements
- **Structured logging**: Provides clear, timestamped logs for monitoring and debugging

## What This Dataproduct Does

1. **Reads CSV data** from input files for different entity types (locations, activities, participants, etc.)
2. **Transforms CSV to RDF** using YARRRML mappings that define how tabular data maps to RDF triples
3. **Validates the RDF** against SHACL shapes to ensure data quality
4. **Loads the RDF** into Fuseki, a SPARQL server, making the data queryable via SPARQL
5. **Tracks data freshness** by comparing input data timestamps with what's already in Fuseki, enabling incremental updates

## Key Features

- ✅ **Production-ready pattern**: Demonstrates the standard transformation pipeline used in production dataproducts
- ✅ **Well-documented**: Comprehensive documentation for both transformation code and output exploration
- ✅ **Best practices**: Includes Python version checking, structured logging, error handling, and incremental processing
- ✅ **Educational**: Designed as a learning resource with clear code structure and extensive comments

## Documentation

This dataproduct includes detailed documentation for different aspects:

- **[Transformation Code Documentation](transformer/transformer-readme.md)**: Comprehensive guide to understanding and modifying the transformation pipeline, including:
  - Main script architecture and patterns
  - Python version compatibility checking
  - Fuseki client usage
  - RDF generation and validation
  - CSV utilities and date comparison
  - Configuration and logging

- **[Linked Data Output Documentation](transformer/linkeddata-output-readme.md)**: Guide to exploring and querying the RDF data stored in Fuseki, including:
  - SPARQL query examples
  - Schema discovery queries
  - Graph management operations
  - Best practices for querying linked data

## Getting Started

This dataproduct is used in the [Data Product Developer Onboarding Documentation](https://uitwisselingsplatform.atlassian.net/wiki/spaces/DDTC/pages/380076045/Demo+dataproduct+opzetten) of the UiTwisselingsplatform.

> **Note**: The Confluence documentation links below refer to documentation in Dutch. The code and inline documentation in this repository are in English.

For detailed information on:
- **Running the transformation code**: See [Running Transformation Code](https://uitwisselingsplatform.atlassian.net/wiki/spaces/DDTC/pages/380272652/Transformatie+code+runnen)
- **Writing transformation code**: See [Writing Transformation Code](https://uitwisselingsplatform.atlassian.net/wiki/spaces/DDTC/pages/379748365/Transformatie+code+schrijven)

## Repository Information

This repository is maintained by publiq in [Bitbucket](https://bitbucket.org/cjsm/demo-dataproduct-9f1ad6510aa76f5a/src/master/).

---

## Repository Maintenance

### Syncing Private and Public Repositories

Changes to this repository must be manually synced with the [public GitHub repository](https://github.com/cultuurnet/uwp-demo-dataproduct).

Technical documentation about this sync process is available in the private [Confluence documentation](https://confluence.publiq.be/display/DDT/Demo+dataproduct%3A+sync+bitbucket+to+github) (publiq internal access required).
