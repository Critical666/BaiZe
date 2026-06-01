"""初始化脚本：首个管理员账户自动创建。

   在应用启动时调用，检查是否存在管理员账户。
   若不存在，则根据环境变量创建一个初始管理员。
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def ensure_init_admin(db_session):
    """
    确保系统中至少存在一个管理员账户。

    Args:
        db_session: SQLAlchemy Session 对象。

    Raises:
        RuntimeError: 数据库查询或用户创建失败时抛出。
    """
    # 延迟导入以避免循环依赖（阶段 A 中 ORM 模型才就绪）
    from app.models.user import User

    existing = db_session.query(User).filter(User.role == "admin").first()
    if existing:
        logger.info("管理员账户已存在，跳过初始化。")
        return

    logger.info("未检测到管理员账户，正在创建初始管理员...")
    admin = User(
        username=settings.init_admin_username,
        email=settings.init_admin_email,
        password_hash="",  # 阶段 A 中由 auth service 替换为真实 hash
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    logger.info(
        "初始管理员创建成功: %s (%s)",
        settings.init_admin_username,
        settings.init_admin_email,
    )
