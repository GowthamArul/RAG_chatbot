import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from llama_index.core.chat_engine.condense_plus_context import CondensePlusContextChatEngine
from configuration.nodeprocessor import DefaultNodePostProcessor


from chat.chat_history import get_chat_history
from chat.document_index import load_index
from llm_model.init_models import get_models
# from config import SYSTEM_PROMPT

retriever = load_index()

async def get_chat_engine(session_id, db: AsyncSession):
    try:
        history = await get_chat_history(session_id, db)
        print(f"Chat history for session {session_id}: {history}")
        return CondensePlusContextChatEngine.from_defaults(
            retriever=retriever,
            llm=get_models()[0],
            chat_history=history,
            system_prompt="You are a helpful assistant answering questions based on company documents.",
            node_postprocessors=[DefaultNodePostProcessor()]
        )
    except Exception as e:
        print(f"Error in get_chat_engine: {e} - {traceback.format_exc()}")
        return None
