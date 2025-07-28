from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

def get_models():
    """
    Initialize and return the LLM and embedding models.
    """
    llm = Ollama(model="mistral:7b")
    embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    return llm, embed_model


