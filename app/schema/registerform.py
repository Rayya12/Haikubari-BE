from pydantic import BaseModel,EmailStr,Field
from typing import Literal

class RegisterForm(BaseModel):
    username:str = Field(min_length=3,max_length=50)
    email:EmailStr
    password:str = Field(min_length=8)
    role: Literal["common","watcher","admin"] = "common"
    photo_url:str | None = None
    file_name:str | None = None
    file_type:str | None = None
    bio:str | None = None
    age:float | None =  Field(default=1,ge=1)
    address:str | None = None
    is_verified:bool
    watcher_status : Literal["pending","suspended","accepted"] = "pending" 