# Angle Photo - Android App

AI-powered multi-angle photo generation app for women.

## Features

- Multi-angle photo generation from a single selfie
- 8 built-in pose presets (45° side, 90° side, low angle, etc.)
- 360° photo generation
- Local photo storage for privacy
- User authentication
- Generation history

## Tech Stack

- **Kotlin** - Primary language
- **Jetpack Compose** - Modern UI toolkit
- **Hilt** - Dependency injection
- **Room** - Local database
- **Retrofit** - Network client
- **Coil** - Image loading
- **CameraX** - Camera functionality

## Project Structure

```
app/
├── src/main/
│   ├── java/com/anglephoto/app/
│   │   ├── data/
│   │   │   ├── database/     # Room database entities and DAOs
│   │   │   ├── local/         # Local preferences (DataStore)
│   │   │   ├── network/       # Retrofit API and models
│   │   │   └── repository/    # Repository pattern
│   │   ├── ui/               # Composable UI screens
│   │   │   └── theme/         # App theme
│   │   ├── di/               # Hilt modules
│   │   └── AnglePhotoApplication.kt
│   └── res/                 # Android resources
├── build.gradle.kts
└── proguard-rules.pro
```

## Building the Project

### Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17
- Android SDK 34

### Build from Android Studio

1. Open the `android` directory in Android Studio
2. Wait for Gradle sync to complete
3. Click Run or Press Shift+F10

### Build from command line

```bash
cd android
./gradlew assembleDebug
```

The APK will be generated at: `app/build/outputs/apk/debug/app-debug.apk`

## Backend Configuration

The app connects to the backend API at `http://127.0.0.1:8000` by default.

To change the API URL, modify `NetworkModule.kt`:
```kotlin
private const val BASE_URL = "http://your-server.com"
```

## Privacy

All user photos and generated results are stored locally on the device. No photos are sent to cloud servers except for the temporary processing required for AI generation.

## Development

### Adding New Features

1. **New API Endpoints**: Add to `ApiService.kt`
2. **New Data Models**: Add to `ApiModels.kt`
3. **New UI Screens**: Add to `ui/` directory
4. **Database Changes**: Update entities and DAOs in `database/`

### Testing

Run unit tests:
```bash
./gradlew test
```

Run instrumented tests:
```bash
./gradlew connectedAndroidTest
```

## License

Copyright © 2025 Angle Photo. All rights reserved.
