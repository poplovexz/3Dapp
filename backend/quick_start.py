import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    print(f"\n{'=' * 60}")
    print(f"Executing: {description}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
        )

        if result.returncode == 0:
            print(f"[OK] {description} succeeded")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"[FAIL] {description} failed")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

    return True


def init_admin_user():
    print("\n" + "=" * 60)
    print("Initializing Admin User")
    print("=" * 60)

    backend_dir = Path(__file__).parent

    import sqlite3

    db_path = backend_dir / "app.db"
    if not db_path.exists():
        print("Database does not exist, skipping admin initialization")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", ("admin",))
    admin_user = cursor.fetchone()

    if not admin_user:
        print("Creating admin account...")
        from auth import get_password_hash

        admin_password = "Admin123"
        password_hash = get_password_hash(admin_password)

        cursor.execute(
            """
            INSERT INTO users (phone_number, email, password_hash, country_code, region, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (None, "admin", password_hash, "", "ADMIN", 1),
        )

        user_id = cursor.lastrowid if cursor.lastrowid is not None else 0
        cursor.execute(
            """
            INSERT INTO user_quotas (user_id, free_generations)
            VALUES (?, ?)
            """,
            (user_id, 999999),
        )

        conn.commit()
        print(f"[OK] Admin account created successfully")
        print(f"  Username: admin")
        print(f"  Password: {admin_password}")
        print(f"  Please change password after login")
    else:
        print("[OK] Admin account already exists")

    conn.close()


def main():
    print("\n" + "=" * 60)
    print("Angle Photo App - Quick Start")
    print("=" * 60)

    backend_dir = Path(__file__).parent

    print("\n1. Checking Python dependencies...")
    if not run_command(
        f'cd "{backend_dir}" && python -c "import requests; print(\'requests OK\')"',
        "Dependency check",
    ):
        print("\nPlease install dependencies first:")
        print(f'cd "{backend_dir}" && pip install -r requirements.txt')
        return

    print("\n2. Initializing database...")
    if not run_command(
        f'cd "{backend_dir}" && python init_db.py', "Database initialization"
    ):
        print("Database initialization failed, but starting server anyway...")

    time.sleep(1)

    print("\n3. Initializing admin account...")
    init_admin_user()

    print("\n4. Starting API service...")
    print("\nService Info:")
    print("  - URL: http://127.0.0.1:8000")
    print("  - API Docs: http://127.0.0.1:8000/docs")
    print("  - Health Check: http://127.0.0.1:8000/health")
    print("\nDefault Admin Account:")
    print("  - Username: admin")
    print("  - Password: Admin123")
    print("\nPress Ctrl+C to stop service")
    print("=" * 60 + "\n")

    try:
        subprocess.run(f'cd "{backend_dir}" && python api_server.py', shell=True)
    except KeyboardInterrupt:
        print("\n\nService stopped")
    except Exception as e:
        print(f"\n\nStartup failed: {e}")


if __name__ == "__main__":
    main()
