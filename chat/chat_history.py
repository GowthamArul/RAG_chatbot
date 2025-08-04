import traceback
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from llama_index.core.llms import ChatMessage as LlamaChatMessage
from llama_index.core.prompts.base import ChatPromptTemplate

from database.chat import ChatMessageModel
from models.chat_models import ChatRequest

async def get_chat_history(session_id, db:AsyncSession, limit:int=6):
    try:
        if not isinstance(session_id, type(None)):
            session_id = uuid.UUID(session_id)

        messages = (await db.execute(
            select(ChatMessageModel)
            .filter(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.message_ts)
            .limit(limit)
        )).scalars().all()

        if not messages:
            print(f"No chat history found for session {session_id}")
            return []
        
        formatted_messages = [
            ("assistant" if str(message.sender_type) == "ASSISTANT" else "user", message.message_text.strip()) for message in messages
        ]
        chat_history = ChatPromptTemplate.from_messages(formatted_messages)
        history = chat_history.message_templates
        return history if history else []
        # return [LlamaChatMessage(role=str(m.sender_type).lower(), content=m.message_text) for m in messages]
    
    except Exception as e:
        print(f"Error in get_chat_history: {e} {traceback.format_exc()}")
        return []

async def save_message(request:ChatRequest, chat_history:dict, db:AsyncSession):

    try:
        if request.session_id is None:
            session_id = uuid.uuid4()
        else:
            session_id = uuid.UUID(request.session_id)  # Validates format
    except ValueError as e:
        raise ValueError(f"Invalid session_id format: {request.session_id}") from e

    try:
        # Ensure session
        session_result = await db.execute(
            select(ChatMessageModel).where(ChatMessageModel.session_id == session_id)
        )
        session_obj: Optional[ChatMessageModel] = session_result.scalars().first()

        user_id = str(request.user_id) if request.user_id else None
        for role, content in chat_history.items():
            print(f"Saving message: {role} - {content}")
            msg = ChatMessageModel(
                session_id=session_obj.session_id if session_obj else session_id,
                sender_type=str(role),
                message_text=str(content.strip()),
                user_id=user_id
            )
            db.add(msg)

        await db.commit()
        return session_obj.session_id if session_obj else session_id
    except Exception as e:
        print(f"Error saving message: {e} {traceback.format_exc()}")


async def get_messages(session_id: str, db: AsyncSession):
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session_id format: {session_id}")
    
    messages = (await db.execute(
        select(ChatMessageModel).where(
            ChatMessageModel.session_id == session_uuid, 
            ChatMessageModel.status != "INACTIVE"
            ).order_by(ChatMessageModel.message_ts)
            )).scalars().all()

    if not messages:
        raise HTTPException(
            status_code=404,
            detail=f"No messages found for session_id: {session_id}"
        )
    
    first_msg, last_msg = messages[0], messages[-1]
    metadata = {
        "user_id": first_msg.user_id,
        "session_id": str(first_msg.session_id),
        "start_message_ts": first_msg.message_ts.isoformat(),
        "last_message_ts": last_msg.message_ts.isoformat(),
        "status": first_msg.status
    }
    
    grouped_messages = []
    temp_pair = {}

    for msg in messages:
        sender = msg.sender_type.casefold()
        if sender == 'user':
            temp_pair = {
                "user": msg.message_text.strip(), 
                "message_ts": msg.message_ts.isoformat()
                }
        elif sender == 'assistant' and temp_pair:
            temp_pair["assistant"] = msg.message_text.strip()
            grouped_messages.append(temp_pair)
            temp_pair = {}
    return {**metadata, "messages": grouped_messages} if grouped_messages else {"messages": []}