import os
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text 

from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import (MetadataFilters, MetadataFilter, FilterOperator)
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from llm_model.init_models import get_models
from configuration.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, SCHEMA_NAME, TABLE_NAME


# PGVectorStore instance
vector_store = PGVectorStore.from_params(
    database=DB_NAME,
    host=DB_HOST,
    password=DB_PASSWORD,
    port=5432,
    user=DB_USER,
    schema_name = SCHEMA_NAME,
    table_name = TABLE_NAME,
    embed_dim=768,
    hybrid_search=True,
    text_search_config = "english",
    hnsw_kwargs={
        "hnsw_ef_construction": 64,
        "hnsw_ef_search": 100,
        "hnsw_m": 16,
        "hnsw_dist_method": "vector_cosine_ops"
        }
)


async def file_already_indexed(all_files:list, db:AsyncSession):

    sql = text("""
        SELECT DISTINCT metadata_ ->> 'file_name' AS file_name
        FROM clara.data_vector_index dvi;
    """)

    result = await db.execute(sql)
    rows = result.fetchall()
    present_files = {row.file_name for row in rows}

    # Find missing files
    missing_files = [f for f in all_files if f not in present_files]
    return missing_files



async def build_index(db:AsyncSession):

    data_dir = "data"
    all_files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    missing_files =  await file_already_indexed(all_files, db)
    new_docs = []

    for file in missing_files:
        file_path = os.path.join(data_dir, file)
        doc = SimpleDirectoryReader(input_files=[file_path]).load_data()
        new_docs.extend(doc)

    if not new_docs:
        print("No new PDFs to index.")
        return None
    
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)
    nodes = splitter.get_nodes_from_documents(
        new_docs, show_progress=False
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(
            nodes,
            embed_model=get_models()[1],
            vector_store=vector_store,
            storage_context=storage_context
        )
    
    return index.as_retriever()


def load_index(query:str, k:int = 10):
    """    Load the index from the vector store and return it as a retriever.
    """
    product_name = re.findall(r'\bNCT\d+\b', query)
    if len(product_name) > 0:
        metadata_filter = MetadataFilters(filters=[
            MetadataFilter(
                            key="product", 
                            value=product_name[0], 
                            operator=FilterOperator.IN
                            )
        ])
    else:
        metadata_filter = MetadataFilters(filters=[])


    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=get_models()[1],
    ).as_retriever(similarity_top_k=k, 
                   vector_store_query_mode= VectorStoreQueryMode.HYBRID,
                   filters = metadata_filter)