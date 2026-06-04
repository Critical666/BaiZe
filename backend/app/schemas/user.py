"""用户相关数据模型。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """注册请求。所有自主注册的用户默认角色为 user。"""

    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """登录请求。"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    """用户信息响应。"""

    model_config = {"from_attributes": True}

    id: str
    username: str
    email: str
    role: Literal["admin", "user"]
    created_at: str

    @field_validator("created_at", mode="before")
    @classmethod
    def _coerce_datetime(cls, v: object) -> str:
        """将 ORM 返回的 datetime 对象转为字符串。"""
        if isinstance(v, datetime):
            return str(v)
        return v


class TokenResponse(BaseModel):
    """登录成功后的 Token 响应。"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserRoleUpdate(BaseModel):
    """管理员修改用户角色（仅 admin 可调用）。"""

    role: Literal["admin", "user"]

