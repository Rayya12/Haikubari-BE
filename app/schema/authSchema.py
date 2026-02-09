from pydantic import BaseModel,Field
from fastapi_users import schemas
import uuid
from typing import Literal

class UserRead(schemas.BaseUser[uuid.UUID]):
    username:str
    role:str
    age:int | None
    photo_url:str |None
    file_name:str |None
    file_type:str |None
    bio:str |None
    address:str |None
    
class UserCreate(schemas.BaseUserCreate):
    username:str
    role: Literal["common","watcher"]
    age: int = Field(default=1,ge=1)
    
class UserUpdate(schemas.BaseUserUpdate):
    username:str
    photo_url:str | None
    file_name : str | None
    file_type : Literal["image"] | None
    bio : str | None
    age: int = Field(default=1,ge=1)
    address : str | None
    
