"""用户相关数据模型。"""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """注册请求。"""

    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """登录请求。"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    """用户信息响应。"""

    id: str
    username: str
    email: str
    role: str
    created_at: str


class TokenResponse(BaseModel):
    """登录成功后的 Token 响应。"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
