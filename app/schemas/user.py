from pydantic import BaseModel, EmailStr


class AdminUserBase(BaseModel):
    name: str
    email: EmailStr


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserLogin(BaseModel):
    email: str
    password: str


class AdminUserResponse(AdminUserBase):
    id: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
