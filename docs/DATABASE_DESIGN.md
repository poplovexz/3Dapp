# 角度拍摄 - 数据库设计文档

## 📋 概述

**存储策略**：
- ✅ 云端数据库：用户账号、配额、API KEY、收入数据
- ❌ 本地数据库：个人照片、生成结果、生成历史（仅APP可访问）

---

## 🗂️ 数据库表设计

### 1. 用户相关表（已存在）

#### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT,
    email TEXT,
    password_hash TEXT NOT NULL,
    country_code TEXT DEFAULT '+86',
    region TEXT DEFAULT 'CN',
    is_admin BOOLEAN DEFAULT 0,
    is_blocked BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    UNIQUE(phone_number, email)
);

CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_region ON users(region);
```

#### user_quotas
```sql
CREATE TABLE user_quotas (
    user_id INTEGER PRIMARY KEY,
    free_generations INTEGER DEFAULT 5,
    used_generations INTEGER DEFAULT 0,
    subscription_level TEXT DEFAULT 'free',
    subscription_expiry TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### verification_codes
```sql
CREATE TABLE verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL,
    code TEXT NOT NULL,
    code_type TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_verification_codes_identifier ON verification_codes(identifier);
CREATE INDEX idx_verification_codes_code ON verification_codes(code);
```

---

### 2. API管理相关表（新增）

#### api_keys
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    encrypted_key TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    monthly_limit INTEGER DEFAULT 10000,
    current_usage INTEGER DEFAULT 0,
    last_rotated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_provider ON api_keys(provider);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

#### api_usage_logs
```sql
CREATE TABLE api_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_id INTEGER NOT NULL,
    user_id INTEGER,
    endpoint TEXT NOT NULL,
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_usage_logs_api_key_id ON api_usage_logs(api_key_id);
CREATE INDEX idx_api_usage_logs_user_id ON api_usage_logs(user_id);
CREATE INDEX idx_api_usage_logs_created_at ON api_usage_logs(created_at);
CREATE INDEX idx_api_usage_logs_success ON api_usage_logs(success);
```

---

### 3. 使用统计相关表（新增）

#### daily_statistics
```sql
CREATE TABLE daily_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE NOT NULL UNIQUE,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    image_generations INTEGER DEFAULT 0,
    video_generations INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    total_revenue_cents INTEGER DEFAULT 0
);

CREATE INDEX idx_daily_statistics_date ON daily_statistics(stat_date);
```

#### package_sales
```sql
CREATE TABLE package_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    package_type TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT NOT NULL,
    is_recurring BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_package_sales_user_id ON package_sales(user_id);
CREATE INDEX idx_package_sales_purchase_date ON package_sales(purchase_date);
CREATE INDEX idx_package_sales_package_type ON package_sales(package_type);
```

---

### 4. 订单相关表（已存在）

#### orders
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_type TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🔒 数据安全策略

### 1. API KEY加密存储

**加密方式**: AES-256
- 密钥：环境变量或主密钥管理系统
- 加密字段：`encrypted_key`
- 原始密钥：管理后台获取后立即加密，不保留明文

### 2. 敏感字段加密

**需要加密的字段**：
- `api_keys.encrypted_key` - API密钥
- `orders.payment_id` - 支付ID（如包含敏感信息）

### 3. 数据访问控制

**RBAC权限**：
- 超级管理员：可以访问所有数据
- 普通管理员：可以访问用户和统计数据
- API KEY管理员：只能管理API KEY
- 财务管理员：只能访问订单和统计数据

### 4. 数据脱敏

**日志记录规则**：
- 记录API调用，但**不记录用户参数**（图片、提示词）
- 只记录端点、时间、状态码
- 记录统计数据（使用量、收入）
- **不记录个人照片数据**

---

## 📊 索引优化

### 创建的索引

```sql
-- 用户表索引
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_region ON users(region);
CREATE INDEX idx_users_last_login ON users(last_login);
CREATE INDEX idx_users_created_at ON users(created_at);

-- API KEY表索引
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_provider ON api_keys(provider);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
CREATE INDEX idx_api_keys_created_at ON api_keys(created_at);

-- API使用日志索引
CREATE INDEX idx_api_usage_logs_api_key_id ON api_usage_logs(api_key_id);
CREATE INDEX idx_api_usage_logs_user_id ON api_usage_logs(user_id);
CREATE INDEX idx_api_usage_logs_created_at ON api_usage_logs(created_at);
CREATE INDEX idx_api_usage_logs_success ON api_usage_logs(success);

-- 统计数据索引
CREATE INDEX idx_daily_statistics_date ON daily_statistics(stat_date);
CREATE INDEX idx_package_sales_user_id ON package_sales(user_id);
CREATE INDEX idx_package_sales_purchase_date ON package_sales(purchase_date);
```

---

## 🔄 数据维护

### 1. 定期清理任务

```sql
-- 清理过期的验证码（每天执行）
DELETE FROM verification_codes 
WHERE expires_at < datetime('now', '-1 day');

-- 清理30天前的API使用日志（每周执行）
DELETE FROM api_usage_logs 
WHERE created_at < datetime('now', '-30 days');

-- 清理90天前的订单数据（每月执行）
DELETE FROM package_sales 
WHERE purchase_date < datetime('now', '-90 days');

-- 清理365天前的统计数据（每月执行）
DELETE FROM daily_statistics 
WHERE stat_date < date('now', '-365 days');
```

### 2. 数据备份策略

- 每日自动备份
- 保留最近30天的备份
- 异地备份（阿里云OSS）

---

## 📝 初始化脚本

### 数据库迁移脚本

```python
# backend/migrations/001_add_api_management.py

import sqlite3
from pathlib import Path

def upgrade():
    """添加API管理相关表"""
    db_path = Path(__file__).parent.parent / "app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建api_keys表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT NOT NULL,
            provider TEXT NOT NULL,
            encrypted_key TEXT NOT NULL,
            key_hash TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            monthly_limit INTEGER DEFAULT 10000,
            current_usage INTEGER DEFAULT 0,
            last_rotated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # 创建api_usage_logs表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key_id INTEGER NOT NULL,
            user_id INTEGER,
            endpoint TEXT NOT NULL,
            request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response_time_ms INTEGER,
            status_code INTEGER,
            success BOOLEAN,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建daily_statistics表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE NOT NULL UNIQUE,
            new_users INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            image_generations INTEGER DEFAULT 0,
            video_generations INTEGER DEFAULT 0,
            api_calls INTEGER DEFAULT 0,
            total_revenue_cents INTEGER DEFAULT 0
        )
    ''')
    
    # 创建package_sales表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS package_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            package_type TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_method TEXT NOT NULL,
            is_recurring BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库迁移001: 添加API管理表 - 完成")

def downgrade():
    """回滚迁移"""
    db_path = Path(__file__).parent.parent / "app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS package_sales')
    cursor.execute('DROP TABLE IF EXISTS daily_statistics')
    cursor.execute('DROP TABLE IF EXISTS api_usage_logs')
    cursor.execute('DROP TABLE IF EXISTS api_keys')
    
    conn.commit()
    conn.close()
    print("数据库迁移001: 回滚完成")

if __name__ == "__main__":
    upgrade()
```

---

## 🔐 安全注意事项

### 1. SQL注入防护
- 所有SQL查询使用参数化查询
- 不使用字符串拼接SQL

### 2. 权限验证
- 所有API端点验证用户身份
- 管理员操作验证管理员权限

### 3. 速率限制
- API调用速率限制
- 防止暴力破解

### 4. 日志审计
- 记录所有管理操作
- 记录API KEY使用情况
- 定期审计日志

---

## 📈 性能优化

### 1. 查询优化
- 使用适当的索引
- 避免全表扫描
- 使用EXPLAIN分析慢查询

### 2. 缓存策略
- API KEY缓存（内存缓存）
- 用户配额缓存
- 统计数据缓存

---

**文档版本**: v1.0
**创建日期**: 2025-01-11
**数据库版本**: SQLite 3.x
