# app/models/like.py

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base import Base


class Like(Base):
    __tablename__ = "likes"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )

    haiku_id = Column(
        UUID(as_uuid=True),
        ForeignKey("haikus.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="likestable")
    haiku = relationship("Haiku", back_populates="likestable")