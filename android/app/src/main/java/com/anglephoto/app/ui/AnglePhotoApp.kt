package com.anglephoto.app.ui

import android.net.Uri
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.anglephoto.app.ui.auth.LoginScreen
import com.anglephoto.app.ui.auth.LoginViewModel
import com.anglephoto.app.ui.camera.CameraScreen
import com.anglephoto.app.ui.camera.CameraViewModel
import com.anglephoto.app.ui.history.HistoryScreen
import com.anglephoto.app.ui.history.HistoryViewModel
import com.anglephoto.app.ui.home.PoseSelectionScreen
import com.anglephoto.app.ui.home.HomeViewModel
import com.anglephoto.app.ui.profile.ProfileScreen
import com.anglephoto.app.ui.profile.ProfileViewModel
import com.anglephoto.app.ui.result.ResultScreen
import com.anglephoto.app.ui.result.ResultViewModel

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Home : Screen("home")
    object Camera : Screen("camera")
    object Result : Screen("result/{jobId}")
    object History : Screen("history")
    object Profile : Screen("profile")
}

@Composable
fun AnglePhotoApp(
    viewModel: MainViewModel = hiltViewModel()
) {
    val isLoggedIn by viewModel.isLoggedIn.collectAsState()

    if (isLoggedIn) {
        MainNavigation()
    } else {
        LoginScreen(
            onLoginSuccess = { viewModel.setLoggedIn(true) }
        )
    }
}

@Composable
fun MainNavigation() {
    var currentScreen by remember { mutableStateOf(Screen.Home.route) }
    var selectedPoseId by remember { mutableIntStateOf(0) }
    var capturedUri by remember { mutableStateOf<Uri?>(null) }
    var currentJobId by remember { mutableStateOf("") }

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = currentScreen == Screen.Home.route || currentScreen == Screen.Camera.route,
                    onClick = { currentScreen = Screen.Home.route },
                    icon = { Text("拍照") },
                    label = { Text("拍照") }
                )
                NavigationBarItem(
                    selected = currentScreen == Screen.History.route,
                    onClick = { currentScreen = Screen.History.route },
                    icon = { Text("历史") },
                    label = { Text("历史") }
                )
                NavigationBarItem(
                    selected = currentScreen == Screen.Profile.route,
                    onClick = { currentScreen = Screen.Profile.route },
                    icon = { Text("我的") },
                    label = { Text("我的") }
                )
            }
        }
    ) { paddingValues ->
        when (currentScreen) {
            Screen.Home.route -> {
                if (selectedPoseId > 0) {
                    currentJobId = "gen_${System.currentTimeMillis()}_$selectedPoseId"
                    currentScreen = Screen.Camera.route
                } else {
                    PoseSelectionScreen(
                        onPoseSelected = { poseId ->
                            selectedPoseId = poseId
                            currentScreen = Screen.Camera.route
                        }
                    )
                }
            }
            Screen.Camera.route -> {
                CameraScreen(
                    onPhotoCaptured = { uri ->
                        capturedUri = uri
                        currentJobId = "gen_${System.currentTimeMillis()}_$selectedPoseId"
                        currentScreen = Screen.Result.route
                    }
                )
            }
            Screen.Result.route -> {
                ResultScreen(
                    jobId = currentJobId,
                    onBack = { currentScreen = Screen.Home.route },
                    onShare = { }
                )
            }
            Screen.History.route -> {
                HistoryScreen(
                    onItemClick = { jobId ->
                        currentJobId = jobId
                        currentScreen = Screen.Result.route
                    }
                )
            }
            Screen.Profile.route -> {
                ProfileScreen(
                    onLogout = { }
                )
            }
        }
    }
}
