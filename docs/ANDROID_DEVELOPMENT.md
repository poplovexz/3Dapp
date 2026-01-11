# 角度拍摄 - 安卓APP开发规范

## 📋 项目信息

**项目名称**: Angle Photo (角度拍摄)
**包名**: com.anglephoto.app
**开发语言**: Kotlin
**最低SDK版本**: API 24 (Android 7.0+)
**目标SDK版本**: API 34 (Android 14)
**开发工具**: Android Studio Hedgehog | 2024.1.1

---

## 🏗️ 项目结构

```
app/
├── build.gradle
├── settings.gradle.kts
├── gradle.properties
├── proguard-rules.pro
├── src/main/java/com/anglephoto/app/
│   ├── MainActivity.kt
│   ├── AppApplication.kt
│   ├── data/
│   │   ├── local/
│   │   │   ├── database/
│   │   │   │   ├── AppDatabase.kt
│   │   │   │   ├── entities/
│   │   │   │   │   ├── UserEntity.kt
│   │   │   │   │   ├── GenerationHistoryEntity.kt
│   │   │   │   │   ├── ApiKeyEntity.kt
│   │   │   ├── dao/
│   │   │   │   ├── UserDao.kt
│   │   │   │   ├── GenerationHistoryDao.kt
│   │   │   │   ├── ApiKeyDao.kt
│   ├── ui/
│   │   ├── auth/
│   │   │   ├── LoginActivity.kt
│   │   │   ├── RegisterActivity.kt
│   │   │   └── ForgotPasswordActivity.kt (可选）
│   │   ├── home/
│   │   │   ├── HomeActivity.kt
│   │   │   └── PoseSelectionFragment.kt
│   │   ├── generate/
│   │   │   ├── ImageUploadFragment.kt
│   │   │   ├── AngleControlFragment.kt
│   │   │   ├── PoseSelectionFragment.kt
│   │   │   ├── GenerationProgressFragment.kt
│   │   │   └── GenerationResultFragment.kt
│   │   ├── result/
│   │   │   ├── ImageDetailActivity.kt
│   │   │   ├── VideoPlayerActivity.kt
│   │   │   └── GenerationHistoryActivity.kt
│   │   ├── profile/
│   │   │   ├── ProfileActivity.kt
│   │   │   ├── SettingsActivity.kt
│   │   │   └── QuotaActivity.kt
│   ├── business/
│   │   ├── auth/
│   │   │   ├── AuthService.kt
│   │   │   ├── SessionManager.kt
│   │   │   └── TokenManager.kt
│   │   ├── generation/
│   │   │   ├── GenerationService.kt
│   │   │   ├── ApiService.kt
│   │   │   └── PoseService.kt
│   │   ├── profile/
│   │   │   ├── ProfileService.kt
│   │   │   └── QuotaService.kt
│   ├── utils/
│   │   ├── ImageUtils.kt
│   │   ├── KeyStoreUtils.kt
│   │   ├── NetworkUtils.kt
│   │   ├── DateUtils.kt
│   │   ├── EncryptionUtils.kt
│   │   └── ToastUtils.kt
│   ├── model/
│   │   ├── User.kt
│   │   ├── Pose.kt
│   │   ├── GenerationRequest.kt
│   │   ├── GenerationResult.kt
│   │   └── ApiKey.kt
│   └── api/
│   │       ├── ApiClient.kt
│   │       ├── AuthApi.kt
│       ├── GenerationApi.kt
│       ├── PoseApi.kt
│   │       └── KeyApi.kt
│   ├── res/
│   │   ├── drawable/
│   │   ├── layout/
│   │   ├── mipmap-xxxhdpi/
│   │   └── values/
│   └── manifest/
```

---

## 🎨 UI设计规范

### 1. 配色方案

```kotlin
// 主色调
val colorPrimary = 0xFF0066CC        // 蓝色
val colorPrimaryDark = 0xFF0055AA   // 深蓝色
val colorAccent = 0xFFFFCC00       // 黄色
val colorBackground = 0xFFF5F7FA     // 浅粉色
val colorSurface = 0xFFFFFFFF      // 白色
val colorSurfaceDark = 0xFFF0F0F0  // 黑色

// 文本色
val colorTextPrimary = 0xFF333333      // 深灰色
val colorTextSecondary = 0xFF666666   // 中灰色
val colorTextHint = 0xFF999999     // 浅灰色

// 语义色
val colorSuccess = 0xFF4CAF50       // 绿色
val colorWarning = 0xFFFF9800       // 橙色
val colorError = 0xFFF44336        // 红色
val colorInfo = 0xFF2196F3        // 蓝色
```

### 2. 字体规范

```kotlin
// 字号体系
val fontFamily = "system-ui"  // 中文: sans-serif

// 字号大小
val textSizeH1 = 24.sp
val textSizeH2 = 20.sp
val textSizeH3 = 18.sp
val textSizeBody = 16.sp
val textSizeCaption = 14.sp
val textSizeButton = 16.sp
val textSizeSmall = 12.sp
```

### 3. 组件规范

#### Card组件
```kotlin
@Composable
fun InfoCard(
    title: String,
    subtitle: String? = null,
    icon: @Composable () -> Unit,
    action: @Composable () -> Unit = {},
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .padding(16.dp)
            .fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        border = CardDefaults.cardBorder,
        elevation = CardDefaults.cardElevation
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape),
                    .background(Color(0xFFF0F0F0)),
                contentAlignment = Alignment.Center
            ) {
                icon()
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                if (subtitle != null) {
                    Text(
                        text = subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = colorTextSecondary
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge,
                    color = colorTextPrimary,
                    fontWeight = FontWeight.Bold
                )
            }
            if (action != null) {
                Spacer(modifier = Modifier.height(16.dp))
                action()
            }
        }
    }
}
```

---

## 🗂️ 数据层设计

### Room数据库

```kotlin
@Entity
data class UserEntity(
    @PrimaryKey
    val id: Long,
    val userId: Int,
    val phone: String? = null,
    val email: String? = null,
    val token: String,
    val freeGenerations: Int,
    val totalGenerations: Int,
    val subscriptionLevel: String,
    val subscriptionExpiry: Long?
)

@Entity
data class GenerationHistoryEntity(
    @PrimaryKey
    val id: Long = 0,
    val timestamp: Long,
    val poseId: String? = null,
    val poseName: String? = null,
    val azimuth: Float,
    val elevation: Float,
    val distance: Float,
    val sourceImagePath: String? = null,
    val resultImagePath: String? = null,
    val is360Video: Boolean = false,
    val isAiGenerated: Boolean = false
)

@Entity
data class ApiKeyEntity(
    @PrimaryKey
    val id: Long = 0,
    val keyName: String,
    val provider: String,
    val encryptedKey: String,
    val isActive: Boolean = true,
    val fetchedAt: Long
)
```

### DAO模式

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insertUser(user: UserEntity): Long

    @Query("SELECT * FROM UserEntity WHERE userId = :userId")
    suspend fun getUserByUserId(userId: Int): UserEntity?

    @Query("UPDATE UserEntity SET token = :token, lastLogin = :lastLogin WHERE userId = :userId")
    suspend fun updateToken(userId: Int, token: String): Int
}

@Dao
interface GenerationHistoryDao {
    @Insert
    suspend fun insertGeneration(history: GenerationHistoryEntity): Long

    @Query("SELECT * FROM GenerationHistoryEntity ORDER BY timestamp DESC")
    suspend fun getAllHistory(): List<GenerationHistoryEntity>

    @Query("SELECT * FROM GenerationHistoryEntity WHERE isAiGenerated = 1 ORDER BY timestamp DESC LIMIT 50")
    suspend fun getAiGenerations(): List<GenerationHistoryEntity>

    @Delete
    suspend fun deleteAll(): Int
}

@Dao
interface ApiKeyDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveApiKey(apiKey: ApiKeyEntity): Long

    @Query("SELECT * FROM ApiKeyEntity WHERE isActive = 1")
    suspend fun getActiveKeys(): List<ApiKeyEntity>

    @Query("UPDATE ApiKeyEntity SET isActive = 0 WHERE keyName = :keyName")
    suspend fun deactivateKey(keyName: String): Int

    @Query("DELETE FROM ApiKeyEntity WHERE keyName = :keyName")
    suspend fun deleteKey(keyName: String): Int
}
```

---

## 🔌 API客户端设计

### API服务定义

```kotlin
object ApiService {
    private const val BASE_URL = "https://api.anglephoto.com"
    private const val TIMEOUT = 30_000 // 30秒

    // 认证API
    suspend fun sendVerificationCode(
        identifier: String,
        codeType: String
    ): Result<ApiResponse>

    suspend fun register(
        phoneNumber: String?,
        email: String?,
        password: String,
        countryCode: String,
        region: String,
        verificationCode: String
    ): Result<AuthResponse>

    suspend fun login(
        identifier: String,
        password: String
    ): Result<AuthResponse>

    suspend fun getUserInfo(): Result<UserResponse>

    // 姿势API
    suspend fun getPoses(category: String? = null): Result<PosesResponse>

    // 生成API
    suspend fun generateImage(request: GenerationRequest): Result<GenerationResponse>

    suspend fun generate360Video(request: VideoRequest): Result<JobResponse>

    // 任务API
    suspend fun getJobStatus(jobId: String): Result<JobStatus>

    // API KEY API
    suspend fun getActiveApiKeys(): Result<ApiKeysResponse>
}
```

### HTTP客户端配置

```kotlin
class HttpClient @Inject constructor(
    private val context: Context
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(TIMEOUT, TimeUnit.MILLISECONDS)
        .readTimeout(TIMEOUT, TimeUnit.MILLISECONDS)
        .writeTimeout(TIMEOUT, TimeUnit.MILLISECONDS)
        .build()

    private val gson = Gson()

    suspend fun <T> post(
        endpoint: String,
        body: Any? = null
        headers: Map<String, String>? = null
    ): Result<T> = withContext(Dispatchers.IO) {
        return try {
            val requestBuilder = RequestBody.Builder()
            if (body != null) {
                val jsonBody = gson.toJson(body)
                requestBuilder = requestBuilder.create(
                    "application/json".toMediaType("application/json"),
                    jsonBody
                )
            }

            val request = Request.Builder()
                .url("$BASE_URL$endpoint")
                .post(requestBuilder)
                .apply {
                    headers?.forEach { (key, value) ->
                        addHeader(key, value)
                }

            val response = client.newCall(request).execute()

            if (!response.isSuccessful) {
                return Result.failure(Exception("HTTP ${response.code}"))
            }

            val responseBody = response.body?.string() ?: ""
            val apiResponse = gson.fromJson(responseBody, object : TypeToken<ApiResponse>())
            
            if (apiResponse.success == false) {
                return Result.failure(Exception(apiResponse.message ?: "请求失败"))
            }

            @Suppress("UNCHECKED_CAST")
            val data = apiResponse.data as? T
            if (data != null) {
                Result.success(data)
            } else {
                Result.failure(Exception("数据为空"))
            }
        } catch (e: Exception) {
            return Result.failure(e)
        }
    }

    suspend fun <T> get(
        endpoint: String,
        headers: Map<String, String>? = null
    ): Result<T> = withContext(Dispatchers.IO) {
        return try {
            val request = Request.Builder()
                .url("$BASE_URL$endpoint")
                .get()
                .apply {
                    headers?.forEach { (key, value) ->
                        addHeader(key, value)
                }

            val response = client.newCall(request).execute()

            if (!response.isSuccessful) {
                return Result.failure(Exception("HTTP ${response.code}"))
            }

            val responseBody = response.body?.string() ?: ""
            val apiResponse = gson.fromJson(responseBody, object : TypeToken<ApiResponse>())
            
            if (apiResponse.success == false) {
                return Result.failure(Exception(apiResponse.message ?: "请求失败"))
            }

            @Suppress("UNCHECKED_CAST")
            val data = apiResponse.data as? T
            if (data != null) {
                Result.success(data)
            } else {
                Result.failure(Exception("数据为空"))
            }
        } catch (e: Exception) {
            return Result.failure(e)
        }
    }
}
```

---

## 🔐 密钥存储管理

```kotlin
object KeyStoreUtils {
    private const val PREF_NAME = "angle_photo_prefs"
    private const val KEY_TOKEN = "auth_token"
    private const val KEY_USER_ID = "user_id"
    private const val KEY_API_KEYS = "api_keys"

    fun saveToken(context: Context, token: String) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_TOKEN, token).apply()
    }

    fun getToken(context: Context): String? {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_TOKEN, null)
    }

    fun saveUserId(context: Context, userId: Int) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().putInt(KEY_USER_ID, userId).apply()
    }

    fun getUserId(context: Context): Int {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return prefs.getInt(KEY_USER_ID, -1)
    }

    fun saveApiKeys(context: Context, apiKeys: String) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_API_KEYS, apiKeys).apply()
    }

    fun getApiKeys(context: Context): List<ApiKey> {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        val json = prefs.getString(KEY_API_KEYS, null) ?: return emptyList()
        val gson = Gson()
        val type = object : TypeToken<List<ApiKey>>()
        return gson.fromJson(json, type) ?: emptyList()
    }

    fun clearToken(context: Context) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().remove(KEY_TOKEN).apply()
        KeyStoreUtils.clearUserId(context)
    }
}
```

---

## 📷 开发工作流程

### 1. 认证模块开发

**任务列表**:
- [ ] 登录页面UI
- [ ] 注册页面UI
- [ ] 验证码输入
- [ ] 密码设置
- [ ] Token管理
- [ ] Session管理
- [ ] 记住密码功能

### 2. 主页开发

**任务列表**:
- [ ] 8个系统预设姿势展示
- [ ] 姿势分类筛选
- [ ] 姿势详情页面
- [ ] 热门姿势推荐

### 3. 生成模块开发

**任务列表**:
- [ ] 图片上传（相机/相册）
- [ ] 图片预览和裁剪
- [ ] 8个预设姿势选择
- [ ] 可选3D角度控制
- [ ] AI API集成
- [ ] 进度显示
- [ ] 结果展示
- [ ] 保存到相册

### 4. 个人中心开发

**任务列表**:
- [ ] 用户信息展示
- [ ] 配额查询
- [ ] 历史记录查看
- [ ] 设置页面
- [ ] 退出登录

---

## ⚠️ 重要开发注意事项

### 1. 安全
- [ ] 所有API调用必须使用HTTPS
- [ ] JWT Token存储在SharedPreferences（使用KeyStoreUtils）
- [ ] API KEY加密存储
- [ ] 敏感信息不记录到日志

### 2. 性能
- [ ] 图片使用Coil 2加载
- [ ] 网络请求使用协程和Flow
- [ ] Room数据库异步操作
- [ ] 图片压缩和缓存

### 3. 用户体验
- [ ] 加载动画
- [ ] 错误提示友好
- [ ] 网络状态提示
- [ ] 离线功能检查

### 4. 权限处理
- [ ] 运行时权限检查
- [ ] 合理的权限请求说明

---

## 🧪 测试规范

### 1. 单元测试
- Repository层测试
- Service层测试
- ViewModel测试

### 2. 集成测试
- UI组件测试
- API集成测试

### 3. 性能测试
- 启动时间 < 3秒
- 页面切换流畅
- 内存占用合理

---

**文档版本**: v1.0
**最后更新**: 2025-01-11
**维护者**: 角度拍摄团队
