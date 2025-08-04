import uvicorn
import traceback

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from llama_index.core.chat_engine.types import StreamingAgentChatResponse

from database.base import engine, get_db
from database.chat import Base
from models.chat_models import ChatRequest
from chat.chat_engine import get_chat_engine
from chat.chat_history import save_message

app = FastAPI()


@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    Purpose: Create Schema and tables if not exist
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield   



app = FastAPI(
    title='Patient Data Management',
    description="The PDM application will help maintain patients' historical medication records and allow doctors to chat with an LLM model to gain insights about the drugs.",
    version= "1.0.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    """
    Welcome message on the application startup
    """
    return {"Welcome to the Chatbot Application": "This application allows you to chat with an LLM model and maintain patient data."}

@app.post("/chat",
          tags=["Messages"],
          summary="Chat with the LLM model")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        chat_engine = await get_chat_engine(request.session_id, db)
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
                yield f"Data: {accumulated_response}\n\n"

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

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)