import traceback
from fastapi import (APIRouter,
                     Depends,
                     HTTPException
                     )
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from llama_index.core.chat_engine.types import StreamingAgentChatResponse

from database.base import get_db
from models.chat_models import ChatRequest
from chat.chat_engine import get_chat_engine
from chat.chat_history import save_message, get_messages

router = APIRouter()

@router.post("/chat",
          tags=["Messages"],
          summary="Chat with the LLM model")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        chat_engine = await get_chat_engine(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing chat engine: {str(e)}")
    
    async def event_generator():
        chat_history = {"USER": request.query}
        accumulated_response = ""
        response_dict = {}
        try:
            streaming_response = chat_engine.stream_chat(request.query)
            if not isinstance(streaming_response, StreamingAgentChatResponse):
                raise HTTPException(status_code=500, detail="Invalid response from chat engine")
            
            for chunk in streaming_response.response_gen:
                accumulated_response += chunk
                yield f"{accumulated_response}\n\n"

            chat_history["ASSISTANT"] = accumulated_response
            session_id = await save_message(request, chat_history, db)

            response_dict["session_id"] = session_id
            response_dict["response"] = accumulated_response
            response_dict['Status'] = "success"
            yield f"Data: {response_dict}\n\n"
            
        except Exception as e:
            error_msg = f"Error occurred while processing your request: {str(e)}"
            print(f"Error in event_generator: {error_msg} - {traceback.format_exc()}")
            yield f"ERROR: {error_msg}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{session_id}",
            tags=["Messages"],
            summary="Get chat history for a session")
async def get_message_by_session_id(session_id: str, db: AsyncSession = Depends(get_db)):
        return await get_messages(session_id, db)