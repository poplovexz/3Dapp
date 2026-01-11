from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets

# 配置
SECRET_KEY = secrets.token_urlsafe(32)  # 生产环境应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码至少8位"

    if len(password) > 32:
        return False, "密码最多32位"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)

    if not (has_upper and has_lower):
        return False, "密码必须包含大小写字母"

    return True, ""


def create_access_token(data: dict) -> str:
    """创建JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    """获取当前用户ID"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    return user_id


async def get_current_admin(user_id: int = Depends(get_current_user)) -> int:
    """获取当前管理员ID"""
    from database import Database

    db = Database()

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    return user_id
