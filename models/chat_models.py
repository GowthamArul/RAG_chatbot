from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str | None = None
    query: str
    user_id: str | None = None
