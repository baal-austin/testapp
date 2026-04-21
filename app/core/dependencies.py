# 依赖注入
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.core.security import verify_password
from app.database import get_db
from app.models.user import User
from app.crud.user import get_user_by_username


# 示例依赖函数
def get_current_user():
    # 实现获取当前用户逻辑
    pass
