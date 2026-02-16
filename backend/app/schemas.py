from pydantic import BaseModel, EmailStr, validator
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]

    @validator('password')
    def password_strength(cls, v):
        if not v or len(v) < 8:
            raise ValueError('password must be at least 8 characters')
        return v


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class QuizStartOut(BaseModel):
    quiz_id: int
    title: str
    data: dict
    require_face_reauth: bool


class QuizSubmitIn(BaseModel):
    quiz_id: int
    answers: dict


class QuizSubmitOut(BaseModel):
    score: int
