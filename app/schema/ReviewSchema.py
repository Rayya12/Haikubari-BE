from pydantic import BaseModel,Field
import uuid

class createReview(BaseModel):
    haiku_id : uuid.UUID
    content: str = Field(...,max_length=100)


