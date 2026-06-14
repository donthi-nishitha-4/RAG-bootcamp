"""Compatibility layer for older import paths.

The live retrieval implementation now lives in
`src.core.database.connection`, but some scripts and historical notes still
refer to `src.core.retriever`. Re-export the public API so both paths work.
"""

from src.core.database.connection import (
    build_vector_index,
    check_table_exists,
    get_connection,
    init_pgvector,
    load_documents,
    retrieve_graph,
    retrieve_hybrid,
    retrieve_similar,
    retrieve_trgm,
)

__all__ = [
    "build_vector_index",
    "check_table_exists",
    "get_connection",
    "init_pgvector",
    "load_documents",
    "retrieve_graph",
    "retrieve_hybrid",
    "retrieve_similar",
    "retrieve_trgm",
]
