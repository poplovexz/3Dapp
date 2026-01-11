package com.anglephoto.app.ui.result

import android.net.Uri
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage

@Composable
fun GenerationResultScreen(
    jobId: String,
    onBack: () -> Unit,
    onShare: (Uri) -> Unit,
    viewModel: ResultViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(jobId) {
        viewModel.loadResult(jobId)
    }

    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        TopAppBar(
            title = { Text("生成结果") },
            navigationIcon = {
                IconButton(onClick = onBack) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "返回"
                    )
                }
            },
            modifier = Modifier.fillMaxWidth()
        )

        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        CircularProgressIndicator()
                        Text(
                            text = "AI 正在生成照片...",
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
            uiState.resultUri != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                         Card(
                            modifier = Modifier.fillMaxWidth(),
                            elevation = CardDefaults.cardElevation(8.dp)
                        ) {
                            AsyncImage(
                                model = uiState.resultUri,
                                contentDescription = "生成的照片",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(8.dp),
                                error = {
                                    Box(
                                        modifier = Modifier
                                            .size(120.dp)
                                            .background(androidx.compose.foundation.background),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = "无法加载图片",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                                        )
                                    }
                                }
                            )

                    Spacer(modifier = Modifier.height(24.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        OutlinedButton(
                            onClick = onBack,
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("重新生成")
                        }

                        Button(
                            onClick = { uiState.resultUri?.let { onShare(it) } },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("分享")
                        }
                    }
                }
            }
            uiState.errorMessage != null -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Card(
                        modifier = Modifier.padding(16.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Error,
                                contentDescription = "错误",
                                tint = MaterialTheme.colorScheme.onErrorContainer,
                                modifier = Modifier.size(64.dp)
                            )
                            Text(
                                text = "生成失败",
                                style = MaterialTheme.typography.headlineMedium,
                                color = MaterialTheme.colorScheme.onErrorContainer
                            )
                            Text(
                                text = uiState.errorMessage ?: "",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onErrorContainer
                            )
                            Button(onClick = onBack) {
                                Text("重试")
                            }
                        }
                    }
                }
            }
        }
    }
}

data class ResultUiState(
    val isLoading: Boolean = false,
    val resultUri: Uri? = null,
    val errorMessage: String? = null
)

@androidx.hilt.lifecycle.HiltViewModel
class ResultViewModel @Inject constructor(
    private val generationRepository: com.anglephoto.app.data.repository.GenerationRepository
) : androidx.lifecycle.ViewModel() {

    private val _uiState = kotlinx.coroutines.flow.MutableStateFlow(ResultUiState())
    val uiState: kotlinx.coroutines.flow.StateFlow<ResultUiState> = _uiState

    fun loadResult(jobId: String) {
        kotlinx.coroutines.viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isLoading = true,
                errorMessage = null
            )
            
            val result = generationRepository.getJobStatus(jobId)
            result.onSuccess { jobStatus ->
                when (jobStatus.status) {
                    "completed" -> {
                         _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            resultUri = null
                        )
                    }
                    "failed" -> {
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            errorMessage = jobStatus.message
                        )
                    }
                    else -> {
                        kotlinx.coroutines.delay(2000)
                        loadResult(jobId)
                    }
                }
            }.onFailure { exception ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = exception.message
                )
            }
        }
    }
}
