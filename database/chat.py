from sqlalchemy import ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import Uuid as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid


Base = declarative_base()


class ChatMessageModel(Base):
    __tablename__ = 'chat_messages'

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    message_ts: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    message_text: Mapped[str] = mapped_column(
        nullable=False
    )
    sender_type: Mapped[str] = mapped_column(
        nullable=False
    )

