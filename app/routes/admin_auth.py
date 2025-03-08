from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.models import AdminUser
from app.schemas.user import Token, AdminUserCreate, AdminUserLogin, AdminUserResponse
from app.utils.jwt_utils import create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user: AdminUserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否存在
    if db.query(AdminUser).filter(AdminUser.name == user.name).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否存在
    if db.query(AdminUser).filter(AdminUser.email == user.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建新用户
    db_user = AdminUser(
        name=user.name,
        email=user.email,
        password_hash=AdminUser.get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 生成访问令牌
    access_token = create_access_token(db_user.id)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(user_data: AdminUserLogin, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.email == user_data.email).first()
    if not user or not AdminUser.verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=AdminUserResponse)
async def read_users_me(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = db.query(AdminUser).filter(AdminUser.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
