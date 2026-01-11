# 角度拍摄 - API接口文档

## 📋 API端点总览

### 基础信息
- **Base URL**: `https://api.anglephoto.com`
- **API版本**: v1
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON

---

## 🔐 认证API

### 1.1 发送验证码

**端点**: `POST /api/v1/auth/send-code`
**说明**: 发送短信或邮箱验证码

**请求体**:
```json
{
  "identifier": "13800138000",  // 手机号或邮箱
  "code_type": "register"     // "register" 或 "login"
}
```

**响应**:
```json
{
  "message": "验证码已发送到手机",
  "success": true
}
```

**错误响应**:
```json
{
  "detail": "发送过于频繁，请1分钟后再试",
  "status_code": 429
}
```

---

### 1.2 用户注册

**端点**: `POST /api/v1/auth/register`
**说明**: 新用户注册（中国用户需手机号+验证码，国际用户需邮箱+验证码）

**请求体**:
```json
{
  "phone_number": "13800138000",  // 中国用户必填
  "email": "user@example.com",       // 国际用户必填
  "password": "Test1234",           // 8位以上，大小写字母
  "country_code": "+86",
  "region": "CN",
  "verification_code": "123456"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 12345,
  "phone_number": "13800138000",
  "email": null,
  "free_generations": 5,
  "message": "注册成功！您有5次免费生成机会"
}
```

---

### 1.3 用户登录

**端点**: `POST /api/v1/auth/login`
**说明**: 使用手机号或邮箱登录

**请求体**:
```json
{
  "identifier": "13800138000",  // 手机号或邮箱
  "password": "Test1234"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 12345,
  "quota": {
    "user_id": 12345,
    "free_generations": 5,
    "used_generations": 0,
    "subscription_level": "free",
    "subscription_expiry": null
  }
}
```

---

### 1.4 获取当前用户信息

**端点**: `GET /api/v1/auth/me`
**认证**: 需要Bearer Token
**说明**: 获取当前登录用户的详细信息

**响应**:
```json
{
  "id": 12345,
  "phone_number": "13800138000",
  "email": null,
  "region": "CN",
  "created_at": "2025-01-11T10:30:00Z",
  "last_login": "2025-01-11T15:45:00Z",
  "quota": {
    "free_generations": 5,
    "used_generations": 2,
    "subscription_level": "free"
    "subscription_expiry": null
  }
}
```

---

## 🎭 姿势管理API

### 2.1 获取所有系统姿势

**端点**: `GET /api/v1/poses`
**认证**: 需要Bearer Token
**说明**: 获取所有可用的系统预设姿势

**查询参数**:
- `category` (可选): 筛选特定分类（瘦脸/气质/可爱/优雅/细节/全身）
- `active_only` (可选): 是否只返回启用的姿势，默认true

**响应**:
```json
{
  "poses": [
    {
      "id": "flattering_side",
      "name": "45°侧颜",
      "name_en": "45° Side View",
      "description": "显瘦显气质，展现下颌线",
      "description_en": "Slimming and elegant, showing jawline",
      "category": "瘦脸系列",
      "category_en": "Slimming",
      "azimuth": 45.0,
      "elevation": 0.0,
      "distance": 1.0,
      "preview_image_url": null,
      "is_active": true,
      "usage_count": 1250
    },
    {
      "id": "profile_view",
      "name": "90°侧颜",
      "name_en": "90° Side View",
      "description": "完美下颌线，优雅侧颜",
      "description_en": "Perfect jawline, elegant side profile",
      "category": "瘦脸系列",
      "category_en": "Slimming",
      "azimuth": 90.0,
      "elevation": 0.0,
      "distance": 1.1,
      "preview_image_url": null,
      "is_active": true,
      "usage_count": 890
    }
    // ... 其他6个姿势
  ]
}
```

---

### 2.2 增加姿势使用次数

**端点**: `POST /api/v1/poses/{pose_id}/increment`
**认证**: 需要Bearer Token
**说明**: 记录用户使用某个姿势的次数

**路径参数**:
- `pose_id`: 姿势ID

**响应**:
```json
{
  "success": true,
  "message": "使用次数已增加",
  "pose_id": "flattering_side",
  "usage_count": 1251
}
```

---

## 🤖 生成API

### 3.1 生成单张图片

**端点**: `POST /api/v1/generate`
**认证**: 需要Bearer Token
**说明**: 使用AI生成单张指定角度的图片

**请求体**:
```json
{
  "pose_id": "flattering_side",  // 可选：系统预设姿势ID
  "azimuth": 45.0,             // 可选：方位角（0-360）
  "elevation": 0.0,             // 可选：仰角（-30~60）
  "distance": 1.0,               // 可选：距离（0.5~2.0）
  "bg_style": "white_studio",   // 背景样式：default/white_studio/green_screen/dark_studio
  "source_image": "data:image/jpeg;base64,...",  // 可选：用户上传的参考图
  "use_ai_key": true            // 是否使用API KEY（如用户配置）
}
```

**响应**:
```json
{
  "result": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDA...",
  "pose_used": {
    "id": "flattering_side",
    "name": "45°侧颜"
    "azimuth": 45.0,
    "elevation": 0.0,
    "distance": 1.0
  },
  "generation_time_ms": 3250,
  "face_similarity": 0.87
}
```

**错误响应**:
```json
{
  "detail": "免费配额已用完，请购买套餐",
  "status_code": 403
}
```

---

### 3.2 生成360度视频

**端点**: `POST /api/v1/generate-360`
**认证**: 需要Bearer Token
**说明**: 生成360度旋转视频

**请求体**:
```json
{
  "duration": 3.0,              // 视频时长（秒）
  "fps": 24,                    // 帧率
  "elevation": 0.0,             // 仰角
  "distance": 1.0,               // 距离
  "bg_style": "white_studio",
  "source_image": "data:image/jpeg;base64,..."
  "use_ai_key": true
}
```

**响应**:
```json
{
  "job_id": "550e8400-e29b-4d89-8c0a-1234567890",
  "status": "queued",
  "estimated_time_seconds": 15,
  "message": "任务已加入队列"
}
```

---

### 3.3 查询任务状态

**端点**: `GET /api/v1/job/{job_id}`
**认证**: 需要Bearer Token
**说明**: 查询生成任务的状态和进度

**路径参数**:
- `job_id`: 任务ID

**响应**:
```json
{
  "job_id": "550e8400-e29b-4d89-8c0a-1234567890",
  "status": "processing",
  "progress": "24/72",  // 已完成帧数/总帧数
  "result": null,
  "created_at": "2025-01-11T10:30:00Z",
  "updated_at": "2025-01-11T10:32:15Z"
}
```

**状态说明**:
- `queued`: 排队中
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消

---

## 🔑 管理后台API

### 4.1 管理员登录

**端点**: `POST /api/v1/admin/login`
**说明**: 管理员登录（需要管理员权限）

**请求体**:
```json
{
  "username": "admin",
  "password": "Admin@123456"
}
```

---

### 4.2 获取用户列表

**端点**: `GET /api/v1/admin/users`
**认证**: 需要Bearer Token（管理员）
**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `search`: 搜索关键词
- `region`: 地区筛选
- `status`: 状态筛选（active/blocked）

**响应**:
```json
{
  "users": [
    {
      "id": 1,
      "phone_number": "13800138000",
      "email": null,
      "region": "CN",
      "created_at": "2025-01-11T10:30:00Z",
      "last_login": "2025-01-11T15:45:00Z",
      "is_admin": false,
      "is_blocked": false,
      "quota": {
        "free_generations": 5,
        "used_generations": 2,
        "subscription_level": "free"
      },
      "total_generations": 156,
      "total_orders": 3
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 20
}
```

---

### 4.3 封禁/解封用户

**端点**: `POST /api/v1/admin/users/{user_id}/block`
**认证**: 需要Bearer Token（管理员）
**请求体**:
```json
{
  "reason": "违反用户协议",
  "blocked": true
}
```

---

### 4.4 调整用户配额

**端点**: `POST /api/v1/admin/users/{user_id}/quota`
**认证**: 需要Bearer Token（管理员）
**请求体**:
```json
{
  "free_generations": 10,
  "subscription_level": "basic"
  "subscription_expiry": "2025-02-11T00:00:00Z"
}
```

---

## 🔑 API KEY管理API

### 5.1 获取API KEY列表

**端点**: `GET /api/v1/admin/api-keys`
**认证**: 需要Bearer Token（管理员）

**响应**:
```json
{
  "api_keys": [
    {
      "id": 1,
      "key_name": "生产环境-Gemini",
      "provider": "gemini",
      "is_active": true,
      "monthly_limit": 10000,
      "current_usage": 3250,
      "created_at": "2025-01-10T10:30:00Z",
      "last_rotated_at": null
    },
    {
      "id": 2,
      "key_name": "生产环境-SiliconFlow",
      "provider": "siliconflow",
      "is_active": true,
      "monthly_limit": 5000,
      "current_usage": 1200,
      "created_at": "2025-01-10T10:30:00Z",
      "last_rotated_at": null
    }
  ]
}
```

---

### 5.2 添加新的API KEY

**端点**: `POST /api/v1/admin/api-keys`
**认证**: 需要Bearer Token（管理员）
**请求体**:
```json
{
  "key_name": "测试环境-Gemini",
  "provider": "gemini",  // gemini 或 siliconflow
  "api_key": "sk-...",  // 明文密钥（服务器会加密存储）
  "monthly_limit": 1000,
  "is_active": true
}
```

**响应**:
```json
{
  "id": 3,
  "key_name": "测试环境-Gemini",
  "provider": "gemini",
  "is_active": true,
  "monthly_limit": 1000,
  "current_usage": 0,
  "created_at": "2025-01-11T10:30:00Z",
  "encrypted_key": "U2FsdGVk...encrypted..."
}
```

---

### 5.3 轮换API KEY

**端点**: `POST /api/v1/admin/api-keys/{key_id}/rotate`
**认证**: 需要Bearer Token（管理员）

**响应**:
```json
{
  "success": true,
  "message": "API KEY已轮换",
  "new_key_id": 3,
  "previous_key_hash": "abc123..."
}
```

---

## 📊 统计API

### 6.1 每日统计

**端点**: `GET /api/v1/admin/statistics/daily`
**认证**: 需要Bearer Token（管理员）
**查询参数**:
- `date`: 统计日期（格式：YYYY-MM-DD）
- `days`: 统计天数（默认7）

**响应**:
```json
{
  "statistics": [
    {
      "date": "2025-01-11",
      "new_users": 125,
      "active_users": 3200,
      "image_generations": 2450,
      "video_generations": 180,
      "api_calls": 4230,
      "total_revenue_cents": 245000
    },
    // ...
  ]
}
```

---

### 6.2 收入统计

**端点**: `GET /api/v1/admin/statistics/revenue`
**认证**: 需要Bearer Token（管理员）
**查询参数**:
- `period`: daily/weekly/monthly
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应**:
```json
{
  "revenue_summary": {
    "total_revenue_cents": 1250000,
    "period_revenue_cents": 150000,
    "period_start": "2025-01-01",
    "period_end": "2025-01-07",
    "growth_rate": "15.2%"
  },
  "breakdown": {
    "free_users": 120,
    "basic_users": 85,
    "professional_users": 45,
    "lifetime_users": 12
  }
}
```

---

## 📦 套餐管理API

### 7.1 获取套餐列表

**端点**: `GET /api/v1/admin/packages`
**认证**: 需要Bearer Token（管理员）

**响应**:
```json
{
  "packages": [
    {
      "id": 1,
      "name": "免费版",
      "price_cents": 0,
      "duration_days": null,
      "free_generations": 5,
      "custom_pose_limit": 1,
      "features": "5次免费生成，1个自定义姿势",
      "is_active": true
    },
    {
      "id": 2,
      "name": "基础版",
      "price_cents": 499,
      "duration_days": 30,
      "free_generations": 50,
      "custom_pose_limit": 5,
      "features": "50次生成/月，5个自定义姿势，无水印",
      "is_active": true
    },
    {
      "id": 3,
      "name": "专业版",
      "price_cents": 999,
      "duration_days": 30,
      "free_generations": 200,
      "custom_pose_limit": 15,
      "features": "200次生成/月，15个自定义姿势，4K分辨率",
      "is_active": true
    },
    {
      "id": 4,
      "name": "终身版",
      "price_cents": 19900,
      "duration_days": null,
      "free_generations": 999999,
      "custom_pose_limit": 999,
      "features": "无限生成，无限自定义姿势，所有功能",
      "is_active": true
    }
  ]
}
```

### 7.2 创建新套餐

**端点**: `POST /api/v1/admin/packages`
**认证**: 需要Bearer Token（管理员）
**请求体**:
```json
{
  "name": "特殊版",
  "price_cents": 799,
  "duration_days": 30,
  "free_generations": 100,
  "custom_pose_limit": 10,
  "features": "100次生成/月，10个自定义姿势",
  "is_active": true
}
```

---

## 🔄 任务轮询API

### 8.1 查询AI生成任务

**端点**: `GET /api/v1/jobs/{job_id}`
**认证**: 需要Bearer Token

**响应**:
```json
{
  "job_id": "550e8400-e29b-4d89-8c0a-1234567890",
  "type": "image_generation",
  "status": "processing",
  "progress": "生成中...",
  "result": null,
  "created_at": "2025-01-11T10:30:00Z",
  "updated_at": "2025-01-11T10:32:15Z",
  "estimated_completion_time": "2025-01-11T10:33:00Z"
}
```

---

## ⚠️ 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|------------|---------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token过期 |
| 403 | Forbidden | 权限不足或配额不足 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

---

## 🔒 安全机制

### 认证方式
- Bearer Token (JWT)
- Token有效期：7天
- Header格式：`Authorization: Bearer <token>`

### 速率限制
- 发送验证码：1分钟1次
- 登录接口：每分钟5次
- 生成接口：每分钟10次
- 管理接口：每分钟30次

### 配额检查
- 用户每次生成前检查配额
- 配额不足返回403
- 免费版5次用完后需要付费

---

## 📝 使用示例

### 完整的用户注册和生成流程

```bash
# 1. 发送验证码
curl -X POST "https://api.anglephoto.com/api/v1/auth/send-code" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "13800138000",
    "code_type": "register"
  }'

# 2. 用户注册
curl -X POST "https://api.anglephoto.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "13800138000",
    "password": "Test1234",
    "country_code": "+86",
    "region": "CN",
    "verification_code": "123456"
  }'

# 3. 获取姿势列表
curl -X GET "https://api.anglephoto.com/api/v1/poses" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 4. 生成图片
curl -X POST "https://api.anglephoto.com/api/v1/generate" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "pose_id": "flattering_side",
    "use_ai_key": true
  }'
```

---

**文档版本**: v1.0
**最后更新**: 2025-01-11
**维护者**: 角度拍摄团队
