"""认证相关路由。"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserRoleUpdate, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_auth_service, require_admin
from app.models.user import User

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse)
def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    """注册新用户，默认 role = user。"""
    try:
        return service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/auth/login", response_model=TokenResponse)
def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    """登录，返回 JWT Token。"""
    try:
        return service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(require_admin)):
    """获取当前用户信息（仅管理员）。"""
    return current_user


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    data: UserRoleUpdate,
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(require_admin),
):
    """修改用户角色（仅管理员可调用）。"""
    try:
        return service.update_role(user_id, data.role, operator_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
