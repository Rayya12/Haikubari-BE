# app/models/haiku.py

import uuid
import datetime

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base import Base


class Haiku(Base):
    __tablename__ = "haikus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(15), nullable=False)
    hashigo = Column(String(5), nullable=False)
    nakasichi = Column(String(7), nullable=False)
    shimogo = Column(String(5), nullable=False)
    description = Column(Text, nullable=True)

    likes = Column(Integer, default=0, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("likes >= 0", name="check_haiku_likes_non_negative"),
    )

    # Relationships
    user = relationship("User", back_populates="haikus")

    likestable = relationship(
        "Like",
        back_populates="haiku",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reviews = relationship(
        "Review",
        back_populates="haiku",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )