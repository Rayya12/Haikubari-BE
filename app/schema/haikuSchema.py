from pydantic import BaseModel, Field
from fastapi_users import schemas
import uuid

class HaikuPost(BaseModel):
    title:str = Field(...,max_length=15)
    hashigo:str = Field(...,max_length=5)
    nakasichi:str = Field(...,max_length=7)
    shimogo:str = Field(...,max_length=5)
    description:str = Field(...,max_length=300)
    user_id: uuid.UUID
    
    