"""共享 Base，确保所有模型注册到同一元数据。"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
