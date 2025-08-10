import traceback
import os

from sqlalchemy.ext.asyncio import AsyncSession

from llama_index.core.chat_engine.condense_plus_context import CondensePlusContextChatEngine
from configuration.nodeprocessor import DefaultNodePostProcessor


from chat.chat_history import get_chat_history
from chat.document_index import load_index
from llm_model.init_models import get_models
from models.chat_models import ChatRequest



async def get_chat_engine(request:ChatRequest, db: AsyncSession):
    try:
        retriever = load_index(request.query)
        with open(os.path.join(os.path.dirname(__file__), 'system_prompt.txt'), 'r') as file:
            system_prompt = file.read().strip()

        history = await get_chat_history(request.session_id, db)
        
        return CondensePlusContextChatEngine.from_defaults(
            retriever=retriever,
            llm=get_models()[0],
            chat_history=history,
            system_prompt=system_prompt,
            node_postprocessors=[DefaultNodePostProcessor()]
        )
    except Exception as e:
        print(f"Error in get_chat_engine: {e} - {traceback.format_exc()}")
        return None
