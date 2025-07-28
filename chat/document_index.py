from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import SimpleDirectoryReader
from llama_index.core.storage import StorageContext

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


def build_index():
    docs = SimpleDirectoryReader("data").load_data()
    
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)
    nodes = splitter.get_nodes_from_documents(
        docs, show_progress=False
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
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=get_models()[1],
    ).as_retriever(similarity_top_k=k)

