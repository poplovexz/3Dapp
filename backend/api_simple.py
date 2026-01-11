"""
认证和姿势API - 简化版本
只包含认证和姿势管理相关的API
"""

import os
import random
import re
import uvicorn
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入自定义模块
from database import Database, db
from auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    validate_password_strength,
    get_current_user,
)
from sms_service import SMSService
from email_service import EmailService

# Configuration
OUTPUT_DIR = "outputs"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


# ========== 数据模型 ==========


class UserRegister(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: constr(min_length=8, max_length=32)
    country_code: str = "+86"
    region: str = "CN"
    verification_code: str


class UserLogin(BaseModel):
    identifier: str
    password: str


class SendVerificationCode(BaseModel):
    identifier: str
    code_type: str


# ========== 辅助函数 ==========


def is_phone_number(identifier: str) -> bool:
    """判断是否为手机号"""
    return re.match(r"^\d{10,15}$", identifier) is not None


def validate_user_requirements(user: UserRegister) -> tuple[bool, str]:
    """验证用户注册要求"""
    # 至少提供手机号或邮箱
    if not user.phone_number and not user.email:
        return False, "请提供手机号或邮箱"

    # 中国用户必须提供手机号
    if user.region == "CN" and not user.phone_number:
        return False, "中国大陆用户必须提供手机号"

    # 国际用户必须提供邮箱
    if user.region != "CN" and not user.email:
        return False, "国际用户必须提供邮箱"

    # 验证密码强度
    is_valid, reason = validate_password_strength(user.password)
    if not is_valid:
        return False, reason

    # 验证手机号格式
    if user.phone_number:
        if user.country_code == "+86":
            # 中国手机号：11位，以1开头
            if not re.match(r"^1[3-9]\d{9}$", user.phone_number):
                return False, "手机号格式不正确"
        else:
            # 其他国家手机号（简化验证）
            if len(user.phone_number) < 10 or not user.phone_number.isdigit():
                return False, "手机号格式不正确"

    return True, ""


# ========== 认证相关API ==========


@app.post("/auth/send-code")
async def send_verification_code(request: SendVerificationCode):
    """发送验证码（注册或登录）"""
    identifier = request.identifier
    code_type = request.code_type

    # 判断是手机号还是邮箱
    is_phone = is_phone_number(identifier)

    if not is_phone:
        # 邮箱格式验证（简化）
        if "@" not in identifier or "." not in identifier:
            raise HTTPException(status_code=400, detail="邮箱格式不正确")

    # 检查频率限制（1分钟内只能发送1次）
    conn = db.get_connection()
    cursor = conn.cursor()

    if is_phone:
        cursor.execute(
            """
            SELECT COUNT(*) FROM verification_codes
            WHERE identifier = ? AND created_at > datetime("now", "-1 minute")
        """,
            (identifier,),
        )
    else:
        cursor.execute(
            """
            SELECT COUNT(*) FROM verification_codes
            WHERE identifier = ? AND created_at > datetime("now", "-1 minute")
        """,
            (identifier,),
        )

    count_result = cursor.fetchone()
    count = count_result[0] if count_result else 0
    conn.close()

    if count >= 1:
        raise HTTPException(status_code=429, detail="发送过于频繁，请1分钟后再试")

    # 生成6位验证码
    code = str(random.randint(100000, 999999))

    # 保存验证码（5分钟有效）
    db.create_verification_code(identifier, code, code_type, expires_minutes=5)

    # 发送验证码
    if is_phone:
        sms_service = SMSService()
        sms_service.send_code(identifier, code)
        return {"message": "验证码已发送到手机"}
    else:
        email_service = EmailService()
        email_service.send_verification_code(identifier, code)
        return {"message": "验证码已发送到邮箱"}


@app.post("/auth/register")
async def register(request: UserRegister):
    """用户注册"""
    # 验证注册要求
    is_valid, reason = validate_user_requirements(request)
    if not is_valid:
        raise HTTPException(status_code=400, detail=reason)

    # 验证验证码
    identifier = request.phone_number or request.email
    is_code_valid = db.verify_code(identifier, request.verification_code, "register")

    if not is_code_valid:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # 检查是否已注册
    existing_user = db.get_user_by_identifier(identifier)
    if existing_user:
        raise HTTPException(status_code=400, detail="该账号已注册")

    # 创建用户
    password_hash = get_password_hash(request.password)
    user_id = db.create_user(
        phone_number=request.phone_number,
        email=request.email,
        password_hash=password_hash,
        country_code=request.country_code,
        region=request.region,
    )

    # 创建配额（5次免费）
    db.create_user_quota(user_id, free_generations=5)

    # 生成token
    access_token = create_access_token(data={"sub": user_id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "phone_number": request.phone_number,
        "email": request.email,
        "free_generations": 5,
        "message": "注册成功！您有5次免费生成机会",
    }


@app.post("/auth/login")
async def login(request: UserLogin):
    """用户登录"""
    # 检查用户是否存在
    db_user = db.get_user_by_identifier(request.identifier)
    if not db_user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 验证密码
    if not verify_password(request.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 更新登录时间
    db.update_last_login(db_user["id"])

    # 生成token
    access_token = create_access_token(data={"sub": db_user["id"]})

    # 获取配额信息
    quota = db.get_user_quota(db_user["id"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user["id"],
        "quota": quota,
    }


@app.get("/auth/me")
async def get_current_user_info(user_id: int = Depends(get_current_user)):
    """获取当前用户信息"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, phone_number, email, region FROM users WHERE id = ?", (user_id,)
    )
    user = cursor.fetchone()

    # 获取配额
    quota = db.get_user_quota(user_id)

    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    columns = [desc[0] for desc in cursor.description]
    user_dict = dict(zip(columns, user))
    user_dict["quota"] = quota

    return user_dict


# ========== 姿势相关API ==========


@app.get("/poses")
async def get_poses(category: Optional[str] = None, active_only: bool = True):
    """获取所有姿势"""
    if category:
        poses = [
            p for p in db.get_all_system_poses(active_only) if p["category"] == category
        ]
    else:
        poses = db.get_all_system_poses(active_only)

    return {"poses": poses}


@app.post("/poses/{pose_id}/increment")
async def increment_pose_usage(pose_id: int):
    """增加姿势使用次数"""
    db.increment_pose_usage(pose_id)
    return {"success": True, "message": "使用次数已增加"}


# ========== 健康检查 ==========


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "angle-photo-api"}


# ========== 启动 ==========

# 初始化服务
sms_service = SMSService()
email_service = EmailService()

if __name__ == "__main__":
    print("=" * 50)
    print("角度拍摄 - 认证和姿势API")
    print("=" * 50)
    print("服务启动中...")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"数据库: {db.db_path}")
    print("=" * 50)

    uvicorn.run(app, host="127.0.0.1", port=8000)
