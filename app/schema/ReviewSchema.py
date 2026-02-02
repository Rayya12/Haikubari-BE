from pydantic import BaseModel,Field
import uuid

class createReview(BaseModel):
    haiku_id : uuid.UUID
    text : str = Field(...,max_length=100)


