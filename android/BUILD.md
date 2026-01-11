# APK 构建指南

## 方法 1: 命令行构建（推荐）

### 前提条件
- Java JDK 已安装
- Android SDK（可通过 Android Studio 或命令行安装）

### 构建步骤

#### 1. 进入项目目录
\`\`\`bash
cd /mnt/e/duanshiping/camera_tool/android
\`\`\`

#### 2. 构建 Debug APK
\`\`\`bash
./gradlew assembleDebug
\`\`\`

#### 3. 构建 Release APK
\`\`\`bash
./gradlew assembleRelease
\`\`\`

#### 4. APK 位置
\`\`\`
Debug: app/build/outputs/apk/debug/app-debug.apk
Release: app/build/outputs/apk/release/app-release.apk
\`\`\`

---

## 方法 2: 使用 GitHub Actions（最简单）

### 优点
- 不需要在本地安装 Android SDK
- 自动化构建
- 可以从网页下载 APK

### 步骤
1. 将代码推送到 GitHub
2. 在项目根目录创建 \`.github/workflows/build.yml\`
3. 提交并推送
4. 在 GitHub Actions 页面下载 APK

---

## 方法 3: 在线构建服务

### 可用服务
- [AppCenter](https://appcenter.ms)
- [Buildozer](https://buildozer.com)
- [Codemagic](https://codemagic.com)

---

## WSL 环境注意事项

### 文件路径问题
在 WSL 中，Windows 文件路径需要转换为 Linux 路径：
- Windows: \`E:\duanshiping\camera_tool\android\`
- WSL: \`/mnt/e/duanshiping/camera_tool/android\`

### 推荐做法
\`\`\`bash
# 使用 WSL 路径
cd /mnt/e/duanshiping/camera_tool/android

# 或使用 Windows 路径（某些工具可能需要）
cd "E:\duanshiping\camera_tool\android"
\`\`\`
