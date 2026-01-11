import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class Database:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "app.db")
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                email TEXT,
                password_hash TEXT NOT NULL,
                country_code TEXT DEFAULT '+86',
                region TEXT DEFAULT 'CN',
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                UNIQUE(phone_number, email)
            )
        """)

        # 用户配额表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_quotas (
                user_id INTEGER PRIMARY KEY,
                free_generations INTEGER DEFAULT 5,
                used_generations INTEGER DEFAULT 0,
                subscription_level TEXT DEFAULT 'free',
                subscription_expiry TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 系统姿势预设表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_poses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_en TEXT,
                description TEXT,
                description_en TEXT,
                category TEXT,
                category_en TEXT,
                azimuth FLOAT NOT NULL,
                elevation FLOAT NOT NULL,
                distance FLOAT NOT NULL,
                preview_image_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 用户自定义姿势表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_poses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                source_image_b64 TEXT,
                azimuth FLOAT,
                elevation FLOAT,
                distance FLOAT,
                is_public BOOLEAN DEFAULT 0,
                price_cents INTEGER DEFAULT 99,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 用户姿势购买记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_pose_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pose_id INTEGER,
                purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price_cents INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (pose_id) REFERENCES user_poses(id)
            )
        """)

        # 验证码表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT NOT NULL,
                code TEXT NOT NULL,
                code_type TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 生成记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pose_id INTEGER,
                pose_type TEXT,
                azimuth FLOAT,
                elevation FLOAT,
                distance FLOAT,
                source_image_b64 TEXT,
                result_url TEXT,
                face_similarity FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 订单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_type TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 套餐表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price_cents INTEGER NOT NULL,
                duration_days INTEGER,
                free_generations INTEGER,
                custom_pose_limit INTEGER,
                features TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # 用户订阅表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_id INTEGER,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    # 用户相关方法
    def create_user(
        self,
        phone_number: str | None,
        email: str | None,
        password_hash: str,
        country_code: str,
        region: str,
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (phone_number, email, password_hash, country_code, region)
            VALUES (?, ?, ?, ?, ?)
        """,
            (phone_number, email, password_hash, country_code, region),
        )
        user_id = cursor.lastrowid if cursor.lastrowid is not None else 0
        conn.commit()
        conn.close()
        return user_id

    def get_user_by_identifier(self, identifier: str) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM users
            WHERE phone_number = ? OR email = ?
        """,
            (identifier, identifier),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def update_last_login(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        """,
            (user_id,),
        )
        conn.commit()
        conn.close()

    # 配额相关方法
    def create_user_quota(self, user_id: int, free_generations: int = 5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_quotas (user_id, free_generations)
            VALUES (?, ?)
        """,
            (user_id, free_generations),
        )
        conn.commit()
        conn.close()

    def get_user_quota(self, user_id: int) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_quotas WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def increment_usage(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE user_quotas
            SET used_generations = used_generations + 1
            WHERE user_id = ?
        """,
            (user_id,),
        )
        conn.commit()
        conn.close()

    # 验证码相关方法
    def create_verification_code(
        self, identifier: str, code: str, code_type: str, expires_minutes: int = 5
    ):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO verification_codes (identifier, code, code_type, expires_at)
            VALUES (?, ?, ?, datetime('now', '+' || ? || ' minutes'))
        """,
            (identifier, code, code_type, expires_minutes),
        )
        conn.commit()
        conn.close()

    def verify_code(self, identifier: str, code: str, code_type: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id FROM verification_codes
            WHERE identifier = ? AND code = ? AND code_type = ?
            AND used = 0 AND expires_at > datetime('now')
        """,
            (identifier, code, code_type),
        )
        row = cursor.fetchone()

        if row:
            # 标记为已使用
            cursor.execute(
                """
                UPDATE verification_codes SET used = 1 WHERE id = ?
            """,
                (row[0],),
            )
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    # 系统姿势相关方法
    def get_all_system_poses(self, active_only: bool = True) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        if active_only:
            cursor.execute(
                "SELECT * FROM system_poses WHERE is_active = 1 ORDER BY category, id"
            )
        else:
            cursor.execute("SELECT * FROM system_poses ORDER BY category, id")
        rows = cursor.fetchall()
        conn.close()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []

    def increment_pose_usage(self, pose_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE system_poses SET usage_count = usage_count + 1 WHERE id = ?
        """,
            (pose_id,),
        )
        conn.commit()
        conn.close()

    # 用户姿势相关方法
    def create_user_pose(
        self,
        user_id: int,
        name: str,
        source_image_b64: str,
        azimuth: float,
        elevation: float,
        distance: float,
        is_public: bool = False,
        price_cents: int = 99,
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_poses (user_id, name, source_image_b64, azimuth, elevation, distance, is_public, price_cents)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                name,
                source_image_b64,
                azimuth,
                elevation,
                distance,
                is_public,
                price_cents,
            ),
        )
        pose_id = cursor.lastrowid if cursor.lastrowid is not None else 0
        conn.commit()
        conn.close()
        return pose_id

    def get_user_poses(self, user_id: int) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_poses WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []

    # 生成记录相关方法
    def create_generation(
        self,
        user_id: int,
        pose_id: Optional[int],
        pose_type: str,
        azimuth: float,
        elevation: float,
        distance: float,
        source_image_b64: Optional[str],
        result_url: str,
        face_similarity: Optional[float] = None,
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO generations (user_id, pose_id, pose_type, azimuth, elevation, distance, source_image_b64, result_url, face_similarity, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+7 days'))
        """,
            (
                user_id,
                pose_id,
                pose_type,
                azimuth,
                elevation,
                distance,
                source_image_b64,
                result_url,
                face_similarity,
            ),
        )
        gen_id = cursor.lastrowid if cursor.lastrowid is not None else 0
        conn.commit()
        conn.close()
        return gen_id

    def get_user_generations(self, user_id: int) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM generations WHERE user_id = ? AND expires_at > datetime('now')
            ORDER BY created_at DESC LIMIT 50
        """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []


# 初始化数据库
db = Database()
