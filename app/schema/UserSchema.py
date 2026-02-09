from pydantic import BaseModel, Field
from typing import Literal


class UserUpdate(BaseModel):
    username:str
    photo_url:str | None
    file_name : str | None
    file_type : Literal["image"] | None
    bio : str | None
    age: int = Field(default=1,ge=1)
    address : str | None