import os
import random
import time
import json
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import uvicorn

from database import Database, db as database
from auth import (
    verify_password,
    get_password_hash,
    validate_password_strength,
    create_access_token,
    get_current_user,
    get_current_admin,
)
from sms_service import SMSService
from email_service import EmailService


app = FastAPI(title="角度拍摄 API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


sms_service = SMSService()
email_service = EmailService()


def generate_code() -> str:
    return str(random.randint(100000, 999999))


class SendCodeRequest(BaseModel):
    identifier: str = Field(..., description="手机号或邮箱")
    type: str = Field("register", description="类型: register, login")


class RegisterRequest(BaseModel):
    identifier: str = Field(..., description="手机号或邮箱")
    code: str = Field(..., description="验证码")
    password: str = Field(..., description="密码")


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="手机号或邮箱")
    password: str = Field(..., description="密码")


class GenerateRequest(BaseModel):
    pose_id: int = Field(..., description="姿势ID")
    source_image_b64: str = Field(..., description="base64编码的源图片")


class Generate360Request(BaseModel):
    source_image_b64: str = Field(..., description="base64编码的源图片")
    frame_count: int = Field(36, description="帧数，默认36帧（每10度一帧）")


class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="管理员用户名")
    password: str = Field(..., description="管理员密码")


class AdminUpdateUserQuotaRequest(BaseModel):
    free_generations: Optional[int] = None
    subscription_level: Optional[str] = None
    subscription_expiry: Optional[str] = None


class AdminCreateAPIKeyRequest(BaseModel):
    provider: str = Field(..., description="服务商: gemini, siliconflow")
    api_key: str = Field(..., description="API密钥")
    priority: int = Field(1, description="优先级")


class AdminCreatePackageRequest(BaseModel):
    name: str = Field(..., description="套餐名称")
    price_cents: int = Field(..., description="价格（分）")
    duration_days: Optional[int] = None
    free_generations: int = Field(..., description="免费生成次数")
    custom_pose_limit: int = Field(10, description="自定义姿势数量限制")
    features: Optional[str] = None


def is_phone_number(identifier: str) -> bool:
    return identifier.isdigit() and len(identifier) == 11


@app.get("/")
def read_root():
    return {"service": "角度拍摄 API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/v1/auth/send-code")
def send_code(request: SendCodeRequest):
    identifier = request.identifier
    code_type = request.type

    is_phone = is_phone_number(identifier)

    if is_phone:
        phone_number = identifier
        code = generate_code()

        try:
            success = sms_service.send_code(phone_number, code)
            if success:
                database.create_verification_code(phone_number, code, "sms")
                return {"success": True, "message": "验证码发送成功"}
            else:
                return {"success": False, "message": "短信发送失败，请稍后重试"}
        except Exception as e:
            return {"success": False, "message": f"发送失败: {str(e)}"}
    else:
        email_address = identifier
        code = generate_code()

        try:
            success = email_service.send_verification_code(email_address, code)
            if success:
                database.create_verification_code(email_address, code, "email")
                return {"success": True, "message": "验证码发送成功"}
            else:
                return {"success": False, "message": "邮件发送失败，请稍后重试"}
        except Exception as e:
            return {"success": False, "message": f"发送失败: {str(e)}"}


@app.post("/api/v1/auth/register")
def register(request: RegisterRequest):
    identifier = request.identifier
    code = request.code
    password = request.password

    is_phone = is_phone_number(identifier)

    password_valid, password_msg = validate_password_strength(password)
    if not password_valid:
        raise HTTPException(status_code=400, detail=password_msg)

    code_type = "sms" if is_phone else "email"
    if not database.verify_code(identifier, code, code_type):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    existing_user = database.get_user_by_identifier(identifier)
    if existing_user:
        raise HTTPException(status_code=400, detail="该账号已注册")

    password_hash = get_password_hash(password)

    if is_phone:
        user_id = database.create_user(
            phone_number=identifier,
            email=None,
            password_hash=password_hash,
            country_code="+86",
            region="CN",
        )
    else:
        user_id = database.create_user(
            phone_number=None,
            email=identifier,
            password_hash=password_hash,
            country_code="",
            region="OTHER",
        )

    database.create_user_quota(user_id, free_generations=8)

    access_token = create_access_token(data={"sub": user_id})

    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "token": access_token,
        },
        "message": "注册成功",
    }


@app.post("/api/v1/auth/login")
def login(request: LoginRequest):
    identifier = request.identifier
    password = request.password

    user = database.get_user_by_identifier(identifier)
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    database.update_last_login(user["id"])

    access_token = create_access_token(data={"sub": user["id"]})

    return {
        "success": True,
        "data": {
            "user_id": user["id"],
            "token": access_token,
            "phone_number": user["phone_number"],
            "email": user["email"],
        },
        "message": "登录成功",
    }


@app.get("/api/v1/auth/me")
def get_me(user_id: int = Depends(get_current_user)):
    user = database.get_user_by_identifier(str(user_id))
    if (
        not user
        and database.get_connection()
        .execute("SELECT * FROM users WHERE id = ?", (user_id,))
        .fetchone()
    ):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
        conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    quota = database.get_user_quota(user_id)
    remaining = (
        (quota["free_generations"] or 0) - (quota["used_generations"] or 0)
        if quota
        else 0
    )

    return {
        "success": True,
        "data": {
            "id": user["id"],
            "phone_number": user["phone_number"],
            "email": user["email"],
            "is_admin": bool(user["is_admin"]),
            "created_at": user["created_at"],
            "remaining_generations": max(remaining, 0),
        },
    }


@app.get("/api/v1/poses")
def get_poses(active_only: bool = True):
    poses = database.get_all_system_poses(active_only=active_only)
    return {"success": True, "data": poses, "count": len(poses)}


@app.post("/api/v1/poses/{pose_id}/increment")
def increment_pose_usage(pose_id: int, user_id: int = Depends(get_current_user)):
    database.increment_pose_usage(pose_id)
    return {"success": True, "message": "使用次数已更新"}


@app.post("/api/v1/generate")
def generate_image(request: GenerateRequest, user_id: int = Depends(get_current_user)):
    quota = database.get_user_quota(user_id)
    if not quota:
        raise HTTPException(status_code=400, detail="用户配额不存在")

    remaining = (quota["free_generations"] or 0) - (quota["used_generations"] or 0)
    if remaining <= 0:
        raise HTTPException(status_code=403, detail="生成次数已用完，请购买套餐")

    poses = database.get_all_system_poses(active_only=True)
    pose = next((p for p in poses if p["id"] == request.pose_id), None)
    if not pose:
        raise HTTPException(status_code=404, detail="姿势不存在")

    database.increment_usage(user_id)

    job_id = f"gen_{int(time.time())}_{user_id}_{request.pose_id}"

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "pose_id": request.pose_id,
            "pose_name": pose["name"],
            "status": "processing",
        },
        "message": "图片生成任务已创建，请在APP本地处理",
    }


@app.post("/api/v1/generate-360")
def generate_360_video(
    request: Generate360Request, user_id: int = Depends(get_current_user)
):
    quota = database.get_user_quota(user_id)
    if not quota:
        raise HTTPException(status_code=400, detail="用户配额不存在")

    remaining = (quota["free_generations"] or 0) - (quota["used_generations"] or 0)
    if remaining < request.frame_count:
        raise HTTPException(
            status_code=403,
            detail=f"需要{request.frame_count}次生成，您剩余{max(remaining, 0)}次",
        )

    database.increment_usage(user_id)

    job_id = f"360_{int(time.time())}_{user_id}"

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "frame_count": request.frame_count,
            "status": "processing",
        },
        "message": "360视频生成任务已创建，请在APP本地处理",
    }


@app.get("/api/v1/job/{job_id}")
def get_job_status(job_id: str, user_id: int = Depends(get_current_user)):
    job_user_id = int(job_id.split("_")[2])
    if job_user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此任务")

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "status": "processing",
            "message": "请在Android APP本地处理AI生成",
        },
    }


@app.post("/api/v1/admin/login")
def admin_login(request: AdminLoginRequest):
    if request.username == "admin":
        admin_user = database.get_user_by_identifier("admin")
        if not admin_user:
            admin_id = database.create_user(
                phone_number=None,
                email="admin",
                password_hash=get_password_hash(request.password),
                country_code="",
                region="ADMIN",
            )
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (admin_id,))
            conn.commit()
            conn.close()
            admin_user = database.get_user_by_identifier("admin")

        if admin_user and verify_password(
            request.password, admin_user["password_hash"]
        ):
            if not admin_user["is_admin"]:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET is_admin = 1 WHERE id = ?", (admin_user["id"],)
                )
                conn.commit()
                conn.close()

            access_token = create_access_token(data={"sub": admin_user["id"]})
            return {
                "success": True,
                "data": {
                    "user_id": admin_user["id"],
                    "token": access_token,
                },
                "message": "管理员登录成功",
            }

    raise HTTPException(status_code=401, detail="管理员账号或密码错误")


@app.get("/api/v1/admin/users")
def get_all_users(admin_id: int = Depends(get_current_admin)):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.*, q.free_generations, q.used_generations, q.subscription_level
        FROM users u
        LEFT JOIN user_quotas q ON u.id = q.user_id
        ORDER BY u.created_at DESC
        LIMIT 100
    """)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    users = [dict(zip(columns, row)) for row in rows]
    conn.close()

    return {"success": True, "data": users, "count": len(users)}


@app.post("/api/v1/admin/users/{user_id}/block")
def block_user(user_id: int, admin_id: int = Depends(get_current_admin)):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="用户不存在")

    cursor.execute(
        "UPDATE users SET password_hash = 'BLOCKED' WHERE id = ?", (user_id,)
    )
    conn.commit()
    conn.close()

    return {"success": True, "message": "用户已封禁"}


@app.post("/api/v1/admin/users/{user_id}/quota")
def update_user_quota(
    user_id: int,
    request: AdminUpdateUserQuotaRequest,
    admin_id: int = Depends(get_current_admin),
):
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_quotas WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="用户配额不存在")

    updates = []
    params = []
    if request.free_generations is not None:
        updates.append("free_generations = ?")
        params.append(request.free_generations)
    if request.subscription_level is not None:
        updates.append("subscription_level = ?")
        params.append(request.subscription_level)
    if request.subscription_expiry is not None:
        updates.append("subscription_expiry = ?")
        params.append(request.subscription_expiry)

    if updates:
        params.append(user_id)
        cursor.execute(
            f"UPDATE user_quotas SET {', '.join(updates)} WHERE user_id = ?", params
        )
        conn.commit()

    conn.close()

    return {"success": True, "message": "用户配额已更新"}


@app.get("/api/v1/admin/api-keys")
def get_all_api_keys(admin_id: int = Depends(get_current_admin)):
    return {"success": True, "data": [], "message": "API密钥管理功能待实现"}


@app.post("/api/v1/admin/api-keys")
def create_api_key(
    request: AdminCreateAPIKeyRequest, admin_id: int = Depends(get_current_admin)
):
    return {"success": True, "message": "API密钥创建功能待实现"}


@app.post("/api/v1/admin/api-keys/{key_id}/rotate")
def rotate_api_key(key_id: int, admin_id: int = Depends(get_current_admin)):
    return {"success": True, "message": "API密钥轮换功能待实现"}


@app.get("/api/v1/admin/statistics/daily")
def get_daily_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin_id: int = Depends(get_current_admin),
):
    return {"success": True, "data": [], "message": "每日统计功能待实现"}


@app.get("/api/v1/admin/statistics/revenue")
def get_revenue_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin_id: int = Depends(get_current_admin),
):
    return {
        "success": True,
        "data": {"total_revenue_cents": 0},
        "message": "收入统计功能待实现",
    }


@app.get("/api/v1/admin/statistics")
def get_all_statistics(admin_id: int = Depends(get_current_admin)):
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE created_at >= date('now', '-7 days')"
    )
    new_users_week = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(used_generations) FROM user_quotas")
    total_generations = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "success": True,
        "data": {
            "total_users": total_users,
            "new_users_week": new_users_week,
            "total_generations": total_generations,
            "active_users_today": 0,
        },
    }


@app.get("/api/v1/admin/packages")
def get_all_packages(admin_id: int = Depends(get_current_admin)):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM subscription_plans WHERE is_active = 1 ORDER BY price_cents"
    )
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    packages = [dict(zip(columns, row)) for row in rows]
    conn.close()

    return {"success": True, "data": packages}


@app.post("/api/v1/admin/packages")
def create_package(
    request: AdminCreatePackageRequest, admin_id: int = Depends(get_current_admin)
):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO subscription_plans (name, price_cents, duration_days, free_generations, custom_pose_limit, features)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            request.name,
            request.price_cents,
            request.duration_days,
            request.free_generations,
            request.custom_pose_limit,
            request.features,
        ),
    )
    package_id = cursor.lastrowid if cursor.lastrowid is not None else 0
    conn.commit()
    conn.close()

    return {
        "success": True,
        "data": {"package_id": package_id},
        "message": "套餐创建成功",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
