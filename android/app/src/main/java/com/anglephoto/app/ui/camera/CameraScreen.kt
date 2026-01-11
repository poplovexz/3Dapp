package com.anglephoto.app.ui.camera

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CameraScreen(
    onPhotoCaptured: (Uri) -> Unit,
    viewModel: CameraViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }

    val uiState by viewModel.uiState.collectAsState()

    val cameraPermission = Manifest.permission.CAMERA
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        viewModel.onPermissionResult(isGranted)
    }

    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { uri ->
        uri?.let {
            viewModel.onPhotoCaptured(it)
            onPhotoCaptured(it)
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let { safeUri ->
            viewModel.onPhotoCaptured(safeUri)
            onPhotoCaptured(safeUri)
        }
    }

    LaunchedEffect(Unit) {
        viewModel.checkPermission(context, cameraPermission)
    }

    Scaffold(
        snackbarHost = {
            SnackbarHost(snackbarHostState)
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            if (uiState.hasPermission) {
        if (uiState.capturedUri != null) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        AsyncImage(
                            model = uiState.capturedUri,
                            contentDescription = "拍摄的照片",
                            modifier = Modifier
                                .size(300.dp)
                                .padding(16.dp)
                        )
                        
                        Spacer(modifier = Modifier.height(24.dp))
                        
                        Text(
                            text = "照片已选择",
                            style = MaterialTheme.typography.titleMedium
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                            Button(onClick = {
                                scope.launch {
                                    val result = snackbarHostState.showSnackbar(
                                        message = "使用这张照片",
                                        actionLabel = "确定",
                                        duration = SnackbarDuration.Short
                                    )
                                }
                                if (result == SnackbarResult.ActionPerformed) {
                                    // Proceed to next step
                                }
                            }) {
                                Text("继续")
                            }
                            
                            OutlinedButton(onClick = {
                                viewModel.resetPhoto()
                            }) {
                                Text("重拍")
                            }
                        }
                    }
                } else {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(24.dp)
                    ) {
                        Card(
                            onClick = {
                                permissionLauncher.launch(cameraPermission)
                            },
                            modifier = Modifier
                                .size(200.dp)
                                .padding(16.dp),
                        ) {
                            Box(
                                modifier = Modifier.fillMaxSize(),
                                contentAlignment = Alignment.Center
                            ) {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Icon(
                                        imageVector = android.compose.material.icons.Icons.Default.CameraAlt,
                                        contentDescription = "拍照",
                                        modifier = Modifier.size(48.dp),
                                        tint = MaterialTheme.colorScheme.primary
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "拍照",
                                        style = MaterialTheme.typography.titleMedium
                                    )
                                }
                            }
                        }
                        
                        Card(
                            onClick = {
                                galleryLauncher.launch("image/*")
                            },
                            modifier = Modifier
                                .size(200.dp)
                                .padding(16.dp),
                        ) {
                            Box(
                                modifier = Modifier.fillMaxSize(),
                                contentAlignment = Alignment.Center
                            ) {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Icon(
                                        imageVector = android.compose.material.icons.Icons.Default.PhotoLibrary,
                                        contentDescription = "从相册选择",
                                        modifier = Modifier.size(48.dp),
                                        tint = MaterialTheme.colorScheme.primary
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "从相册选择",
                                        style = MaterialTheme.typography.titleMedium
                                    )
                                }
                            }
                        }
                    }
                }
            } else {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Text(
                        text = "需要相机权限才能拍摄照片",
                        style = MaterialTheme.typography.bodyLarge
                    )
                    
                    Button(onClick = {
                        permissionLauncher.launch(cameraPermission)
                    }) {
                        Text("授予权限")
                    }
                }
            }
        }
    }
}

data class CameraUiState(
    val hasPermission: Boolean = false,
    val capturedUri: Uri? = null
)

@androidx.hilt.lifecycle.HiltViewModel
class CameraViewModel @Inject constructor() : androidx.lifecycle.ViewModel() {
    
    private val _uiState = kotlinx.coroutines.flow.MutableStateFlow(CameraUiState())
    val uiState: kotlinx.coroutines.flow.StateFlow<CameraUiState> = _uiState

    fun checkPermission(context: Context, permission: String) {
        val hasPermission = ContextCompat.checkSelfPermission(
            context,
            permission
        ) == PackageManager.PERMISSION_GRANTED
        _uiState.value = _uiState.value.copy(hasPermission = hasPermission)
    }

    fun onPermissionResult(isGranted: Boolean) {
        _uiState.value = _uiState.value.copy(hasPermission = isGranted)
    }

    fun onPhotoCaptured(uri: Uri) {
        _uiState.value = _uiState.value.copy(capturedUri = uri)
    }

    fun resetPhoto() {
        _uiState.value = _uiState.value.copy(capturedUri = null)
    }
}
