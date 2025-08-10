import uvicorn 
import warning

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.schema import CreateSchema

from database.base import engine
from database.chat import ClaraBase
from router import chatapi

warning.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI()


@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    Purpose: Create Schema and tables if not exist
    """
    async with engine.connect() as connection:
        if ClaraBase.metadata.schema and ClaraBase.metadata.schema != "public":
            await connection.execute(CreateSchema(ClaraBase.metadata.schema, if_not_exists=True))
    async with engine.begin() as conn:
        await conn.run_sync(ClaraBase.metadata.create_all)
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


app.include_router(chatapi.router, prefix='/chat')


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)