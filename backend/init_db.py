import sqlite3
import json
from pathlib import Path
from database import Database


def init_database():
    """初始化数据库，插入系统预设姿势"""
    db_path = Path(__file__).parent / "app.db"

    Database(db_path=str(db_path)).init_db()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 读取系统预设姿势数据
    poses_file = Path(__file__).parent / "poses.json"
    with open(poses_file, "r", encoding="utf-8") as f:
        poses_data = json.load(f)

    # 插入系统预设姿势
    for pose in poses_data["presets"]:
        cursor.execute(
            """
            INSERT OR IGNORE INTO system_poses
            (id, name, name_en, description, description_en, category, category_en,
             azimuth, elevation, distance, preview_image_url, is_active, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                str(pose.get("id", "")),
                pose["name"],
                pose.get("name_en", ""),
                pose["description"],
                pose.get("description_en", ""),
                pose["category"],
                pose.get("category_en", ""),
                pose["azimuth"],
                pose["elevation"],
                pose["distance"],
                pose.get("preview_image_url", ""),
                1 if pose.get("is_active", True) else 0,
                pose.get("usage_count", 0),
            ),
        )

    # 创建初始套餐
    subscription_plans = [
        {
            "name": "免费版",
            "price_cents": 0,
            "duration_days": None,
            "free_generations": 5,
            "custom_pose_limit": 1,
            "features": "5次免费生成，1个自定义姿势",
            "is_active": 1,
        },
        {
            "name": "基础版",
            "price_cents": 499,
            "duration_days": 30,
            "free_generations": 50,
            "custom_pose_limit": 5,
            "features": "50次生成/月，5个自定义姿势，无水印",
            "is_active": 1,
        },
        {
            "name": "专业版",
            "price_cents": 999,
            "duration_days": 30,
            "free_generations": 200,
            "custom_pose_limit": 15,
            "features": "200次生成/月，15个自定义姿势，4K分辨率",
            "is_active": 1,
        },
        {
            "name": "终身版",
            "price_cents": 19900,
            "duration_days": None,
            "free_generations": 999999,
            "custom_pose_limit": 999,
            "features": "无限生成，无限自定义姿势，所有功能",
            "is_active": 1,
        },
    ]

    for plan in subscription_plans:
        cursor.execute(
            """
            INSERT OR IGNORE INTO subscription_plans
            (name, price_cents, duration_days, free_generations, custom_pose_limit, features, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                plan["name"],
                plan["price_cents"],
                plan["duration_days"],
                plan["free_generations"],
                plan["custom_pose_limit"],
                plan["features"],
                plan["is_active"],
            ),
        )

    conn.commit()
    conn.close()

    print("数据库初始化完成！")
    print(f"- 插入了 {len(poses_data['presets'])} 个系统预设姿势")
    print(f"- 创建了 {len(subscription_plans)} 个套餐")


if __name__ == "__main__":
    init_database()
