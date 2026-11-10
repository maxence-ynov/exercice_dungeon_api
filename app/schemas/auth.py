from pydantic import BaseModel, Field, ConfigDict


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)


class PlayerRead(BaseModel):
    id: int
    username: str


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
