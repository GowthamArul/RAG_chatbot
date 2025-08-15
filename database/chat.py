from sqlalchemy import ForeignKey, DateTime, MetaData, Text
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.types import Uuid as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from configuration.config import SCHEMA_NAME


class ClaraBase(DeclarativeBase):
    metadata = MetaData(
        schema=SCHEMA_NAME,
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(columns_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )
    type_annotation_map = {str:Text, datetime:DateTime(timezone=True)}

class ChatMessageModel(ClaraBase):
    __tablename__ = 'chat_messages'

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index = True
    )
    message_ts: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    message_text: Mapped[str] = mapped_column(
        nullable=False
    )
    sender_type: Mapped[str] = mapped_column(
        nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        nullable=True, index=True
        )
    status: Mapped[str] = mapped_column(
        nullable=True, default="ACTIVE", index=True)
