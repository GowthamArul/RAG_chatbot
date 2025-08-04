import os

from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import (MetadataFilters, MetadataFilter, FilterOperator)
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text 
import asyncio

from llm_model.init_models import get_models


# PGVectorStore instance
vector_store = PGVectorStore.from_params(
    database="pgvector_db",
    host="localhost",
    password="password",
    port=5432,
    user="myuser",
    embed_dim=768,
)


async def file_already_indexed(all_files:list, db:AsyncSession):

    sql = text("""
        SELECT DISTINCT metadata_ ->> 'file_name' AS file_name
        FROM data_llamaindex;
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


def load_index(k:int = 3):
    """    Load the index from the vector store and return it as a retriever.
    """

    filters = MetadataFilters(filters=[
        MetadataFilter(key="product", value="widget-x", operator=FilterOperator.IN)
    ])


    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=get_models()[1],
    ).as_retriever(similarity_top_k=k, vector_store_query_mode= VectorStoreQueryMode.HYBRID) # , filters=filters
