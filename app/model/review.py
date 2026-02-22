from sqlalchemy import Column, UUID, ForeignKey, DateTime, Integer,Text,CheckConstraint
from sqlalchemy.orm import relationship
import uuid
import datetime
from app.model.base import Base



class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id",ondelete="CASCADE"), nullable=False, index=True)
    haiku_id = Column(UUID(as_uuid=True), ForeignKey("haikus.id",ondelete="CASCADE"),nullable=False, index= True)
    likes = Column(Integer,default=0)
    created_at = Column(DateTime,default=datetime.datetime.utcnow)
    content = Column(Text,nullable=False)
    
    __table_args__ = (
        CheckConstraint('likes >= 0', name='check_likes_non_negative'),
        CheckConstraint("char_length(content) <= 300",name="content max 300")
    )
    
    user = relationship("User",back_populates="reviews")
    haiku = relationship("Haiku",back_populates="reviews")