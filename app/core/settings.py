from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL : str = Field(alias="DIRECT_URL")
    
    SQL_ECHO : bool = False
    
    model_config = SettingsConfigDict(
        env_file= ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
settings = Settings()