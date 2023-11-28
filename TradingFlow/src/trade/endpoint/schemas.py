from enum import Enum

from pydantic import BaseModel, EmailStr


class Roles(Enum):
    user = "user"
    admin = "admin"


class UserSchemaIn(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserSchemaOut(UserSchemaIn):
    is_active: bool = False

    class Config:
        orm_mode = True
