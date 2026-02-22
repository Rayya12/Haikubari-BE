from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL : str = Field(alias="DIRECT_URL")
    IMAGEKIT_PRIVAT_KEY : str = Field(alias="IMAGE_KIT_PRIVATE_KEY") 
    OTP_TTL_SECONDS : str = Field(alias="OTP_TTL_SECONDS")
    OTP_SECRET : str = Field(alias="SECRET")
    GMAIL_REFRESH_TOKEN : str = Field(alias="GMAIL_REFRESH_TOKEN")
    GMAIL_CLIENT_ID : str = Field(alias="GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET : str = Field(alias="GMAIL_CLIENT_SECRET")
    
    
    
    
    SQL_ECHO : bool = False
    
    model_config = SettingsConfigDict(
        env_file= ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
settings = Settings()

