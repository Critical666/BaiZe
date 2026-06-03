"""FastAPI 依赖注入项。"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.knowledge_service import KnowledgeService
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService
from app.services.stats_service import StatsService

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从请求 Header 中解析 JWT，返回当前用户对象。"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求当前用户为管理员，否则返回 403。"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可执行此操作",
        )
    return current_user


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_knowledge_service(db: Session = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db=db)


def get_stats_service(db: Session = Depends(get_db)) -> StatsService:
    return StatsService(db)
