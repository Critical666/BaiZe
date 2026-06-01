"""认证相关路由。"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.api.deps import get_auth_service

router = APIRouter()


@router.post("/auth/register")
def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    """注册新用户，默认 role = user。"""
    try:
        return service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/auth/login")
def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    """登录，返回 JWT Token。"""
    try:
        return service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
