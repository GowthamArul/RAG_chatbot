import traceback
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from llama_index.core.llms import ChatMessage as LlamaChatMessage

from database.chat import ChatMessageModel

async def get_chat_history(session_id, db:AsyncSession, limit:int=3):
    try:
        messages = (await db.execute(
            select(ChatMessageModel)
            .filter(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.message_ts) # Assuming you have a timestamp for ordering
            .limit(limit) # <-- Added limit here
        )).scalars().all()
        if not messages:
            print(f"No chat history found for session {session_id}")
            return []
        return [LlamaChatMessage(role=str(m.sender_type).lower(), content=m.message_text) for m in messages]
    
    except Exception as e:
        print(f"Error in get_chat_history: {e} {traceback.format_exc()}")
        return []

async def save_message(session_id:str, chat_history:dict, db:AsyncSession):
    try:
        # Ensure session
        session_result = await db.execute(
            select(ChatMessageModel).where(ChatMessageModel.session_id == session_id)
        )
        session_obj: Optional[ChatMessageModel] = session_result.scalars().first()
        if not session_obj:
            new_session_id=uuid.uuid4()
            for role, content in chat_history.items():
                print(f"Saving message: {role} - {content}")
                msg = ChatMessageModel(
                    session_id=new_session_id,
                    sender_type=str(role),
                    message_text=str(content.strip())
                )
                db.add(msg)
        else:
            for role, content in chat_history.items():
                print(f"Saving message: {role} - {content}")
                msg = ChatMessageModel(
                    session_id=session_obj.session_id,
                    sender_type=str(role),
                    message_text=str(content.strip())
                )
                db.add(msg)
        

        await db.commit()
        return new_session_id if not session_obj else session_obj.session_id
    except Exception as e:
        print(f"Error saving message: {e} {traceback.format_exc()}")