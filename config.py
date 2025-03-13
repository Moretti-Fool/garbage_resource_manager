from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    BASE_URL: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    VERIFICATION_TOKEN_EXPIRE: int
    SECRET_KEY: str 
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    SECRET_KEY_GOOGLE_AUTH: str
    
    
    
    
    class Config:
        env_file = ".env"

settings =  Settings()