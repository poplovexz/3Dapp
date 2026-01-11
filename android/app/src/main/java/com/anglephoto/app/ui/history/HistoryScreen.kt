package com.anglephoto.app.ui.history

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun HistoryScreen(
    onItemClick: (String) -> Unit,
    viewModel: HistoryViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadHistory()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("生成历史") },
                modifier = Modifier.fillMaxWidth()
            )
        }
    ) { paddingValues ->
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            uiState.generations.isEmpty() -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.History,
                            contentDescription = "历史",
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
                        )
                        Text(
                            text = "暂无生成历史",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                        Text(
                            text = "拍摄照片开始第一次生成吧",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
                        )
                    }
                }
            }
            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(uiState.generations) { generation ->
                        GenerationItem(
                            generation = generation,
                            onClick = { onItemClick(generation.id) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun GenerationItem(
    generation: com.anglephoto.app.data.database.GenerationEntity,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (generation.resultImageUri != null) {
                AsyncImage(
                    model = generation.resultImageUri,
                    contentDescription = "生成的照片",
                    modifier = Modifier
                        .size(80.dp, 80.dp)
                        .clip(androidx.compose.foundation.shape.CircleShape),
                    error = {
                        Box(
                            modifier = Modifier
                                .size(80.dp, 80.dp)
                                .clip(androidx.compose.foundation.shape.CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Image,
                                contentDescription = null,
                                modifier = Modifier.size(32.dp),
                                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
                            )
                        }
                    }
                )
            } else {
                Box(
                    modifier = Modifier
                        .size(80.dp, 80.dp)
                        .clip(androidx.compose.foundation.shape.CircleShape),
                    contentAlignment = Alignment.Center,
                    background = androidx.compose.foundation.background
                ) {
                    Icon(
                        imageVector = Icons.Default.Image,
                        contentDescription = "占位图",
                        modifier = Modifier.size(32.dp),
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = "照片生成",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = formatDate(generation.createdAt),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                
                if (generation.poseType == "360") {
                    Surface(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = "360° 生成",
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                } else {
                    Surface(
                        color = MaterialTheme.colorScheme.secondaryContainer,
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = "单张生成",
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                    }
                }
                
                if (generation.status != "completed") {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "生成中...",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "查看详情",
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
        }
    }
}

private fun formatDate(timestamp: Long): String {
    val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
    return sdf.format(Date(timestamp))
}

data class HistoryUiState(
    val isLoading: Boolean = false,
    val generations: List<com.anglephoto.app.data.database.GenerationEntity> = emptyList(),
    val errorMessage: String? = null
)

@androidx.hilt.lifecycle.HiltViewModel
class HistoryViewModel @Inject constructor(
    private val generationRepository: com.anglephoto.app.data.repository.GenerationRepository,
    private val userRepository: com.anglephoto.app.data.repository.UserRepository
) : androidx.lifecycle.ViewModel() {

    private val _uiState = kotlinx.coroutines.flow.MutableStateFlow(HistoryUiState())
    val uiState: kotlinx.coroutines.flow.StateFlow<HistoryUiState> = _uiState

    fun loadHistory() {
        kotlinx.coroutines.viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {
                val userId = userRepository.getUserId()?.toIntOrNull() ?: return@launch
                val generations = generationRepository.getLocalGenerations()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    generations = generations
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = e.message
                )
            }
        }
    }
}
