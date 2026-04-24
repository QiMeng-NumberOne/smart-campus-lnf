from pydantic import BaseModel


class LoginRequest(BaseModel):
    account: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    phone: str | None = None
    student_id: str | None = None


class UpdateProfileRequest(BaseModel):
    username: str | None = None
    phone: str | None = None
    student_id: str | None = None
    avatar: str | None = None
    grade: str | None = None
    college: str | None = None
    major: str | None = None
