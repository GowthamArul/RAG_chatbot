from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from llama_index.core.chat_engine.types import StreamingAgentChatResponse

import uvicorn
import traceback
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

@app.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        chat_engine = await get_chat_engine(request.session_id, db)
        
        async def event_generator():
            try:
                chat_history = {"USER": request.query}
                streaming_response = chat_engine.stream_chat("Tell me about the Deep Singer")
                assert isinstance(streaming_response, StreamingAgentChatResponse)
                response_dict = {'accumulated_response' : [""]}
                try:
                    for chunk in streaming_response.response_gen:
                        response_dict["accumulated_response"][0] += chunk
                        yield f"Data: {response_dict['accumulated_response']}\n\n"
                    chat_history["ASSISTANT"] = response_dict["accumulated_response"][0]
                    session_id = await save_message(request.session_id, chat_history, db)
                    response_dict["session_id"] = session_id
                    yield f"Data: {response_dict}\n\n"
                except Exception as e:
                    print(f"Error in event_generator: {e}")
                    yield f"data: Error occurred: {str(e)}\n\n"
            except Exception as e:
                print(f"Error in event_generator: {e} {traceback.format_exc()}")
                yield "data: Error occurred while processing your request.\n\n"

            

        return StreamingResponse(event_generator(), media_type="text/event-stream")
        # return {"response": f"Debbing mode is enabled. Please check the logs for more details.{chat_engine}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)