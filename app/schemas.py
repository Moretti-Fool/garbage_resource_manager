from pydantic_settings import BaseSettings

class UserCreate(BaseSettings):
    email: str
    password: str