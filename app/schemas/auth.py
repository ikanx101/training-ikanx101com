from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    bio: Optional[str] = None
    security_question: str
    security_answer: str

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifySecurityAnswer(BaseModel):
    email: str
    security_answer: str

class ResetPasswordRequest(BaseModel):
    email: str
    security_answer: str
    new_password: str
