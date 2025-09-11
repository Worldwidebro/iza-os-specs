# Chapter 3: Knowledge Architecture

This chapter details the strategy for building and maintaining the Iza OS knowledge graph.

## 1. Core Technologies

- **Neo4j:** The graph database for storing entities and relationships.
- **Qdrant:** The vector database for storing embeddings and enabling semantic search.
- **Pathway:** The real-time ETL and RAG framework, serving as the backbone for data ingestion and processing.
- **Activepieces:** The central MCP gateway for connecting to various external data sources.

## 2. Data Ingestion Pipelines (ETL with Pathway)

All data ingestion into the knowledge graph and vector stores will be orchestrated by **Pathway**.

- **Pathway Connectors:** Pathway will connect to external data sources (e.g., Apple Notes, Google Drive, GitHub, Calendar) via Activepieces' MCPs or directly if a Pathway connector exists.
- **Real-time Transformations:** Pathway will perform real-time transformations (e.g., parsing, cleaning, structuring) on incoming data streams.
- **Embedding Generation:** Pathway's LLM helpers will generate embeddings for text data, which will then be stored in Qdrant.
- **Knowledge Graph Population:** Pathway will extract entities and relationships from processed data and ingest them into Neo4j.

## 3. Retrieval-Augmented Generation (RAG with Pathway)

Pathway will power the core RAG pipeline, ensuring Claude has access to the most relevant and up-to-date information.

- **Real-time Vector Index:** Pathway maintains an in-memory, real-time vector index (backed by Qdrant) for fast semantic search.
- **Contextual Retrieval:** When Claude needs context for a task, Pathway will retrieve relevant information from Neo4j (structured knowledge) and Qdrant (semantic knowledge).
- **Dynamic Context Building:** The `ContextManager` will leverage Pathway to build rich, dynamic contexts for Claude, combining structured data, unstructured text, and real-time insights.

## 4. Knowledge Graph Auto-Population (Enhanced with Pathway)

The `ClaudeKGBuilder` will utilize Pathway to continuously update the knowledge graph.

- **Automated Extraction:** Pathway pipelines will automatically extract new entities and relationships from ongoing conversations and data streams.
- **Schema Evolution:** Pathway can assist in identifying new entity types and relationships, supporting the auto-evolution of the knowledge graph schema.
