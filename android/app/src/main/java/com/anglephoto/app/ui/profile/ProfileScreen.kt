package com.anglephoto.app.ui.profile

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.anglephoto.app.data.repository.UserRepository

@Composable
fun ProfileScreen(
    onLogout: () -> Unit,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadUserInfo()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("我的") },
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
            else -> {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        UserHeader(
                            phoneNumber = uiState.userInfo?.phone_number,
                            email = uiState.userInfo?.email
                        )
                    }

                    item {
                        StatsCard(
                            remainingGenerations = uiState.userInfo?.remaining_generations ?: 0
                        )
                    }

                    item {
                        MenuItem(
                            icon = Icons.Default.ShoppingCart,
                            title = "购买套餐",
                            description = "升级以获得更多生成次数",
                            onClick = { }
                        )
                    }

                    item {
                        MenuItem(
                            icon = Icons.Default.History,
                            title = "生成历史",
                            description = "查看所有生成的照片",
                            onClick = { }
                        )
                    }

                    item {
                        MenuItem(
                            icon = Icons.Default.Settings,
                            title = "设置",
                            description = "应用设置",
                            onClick = { }
                        )
                    }

                    item {
                        MenuItem(
                            icon = Icons.Default.Help,
                            title = "帮助与反馈",
                            description = "使用帮助和问题反馈",
                            onClick = { }
                        )
                    }

                    item {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                    }

                    item {
                        OutlinedButton(
                            onClick = onLogout,
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = MaterialTheme.colorScheme.error
                            )
                        ) {
                            Text(
                                text = "退出登录",
                                color = MaterialTheme.colorScheme.error
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun UserHeader(
    phoneNumber: String?,
    email: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(CircleShape),
                background = androidx.compose.foundation.background
            ) {
                Icon(
                    imageVector = Icons.Default.Person,
                    contentDescription = "用户头像",
                    modifier = Modifier.fillMaxSize(),
                    tint = MaterialTheme.colorScheme.primary
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column {
                Text(
                    text = phoneNumber ?: email ?: "用户",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = if (phoneNumber != null) "手机号" else "邮箱",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }
        }
    }
}

@Composable
fun StatsCard(
    remainingGenerations: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            Text(
                text = "剩余生成次数",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "$remainingGenerations 次",
                style = MaterialTheme.typography.displayLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            LinearProgressIndicator(
                progress = { remainingGenerations / 10f },
                modifier = Modifier.fillMaxWidth(),
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun MenuItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                modifier = Modifier.size(32.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "进入",
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
        }
    }
}

data class ProfileUiState(
    val isLoading: Boolean = false,
    val userInfo: com.anglephoto.app.data.network.UserInfo? = null
)

@androidx.hilt.lifecycle.HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : androidx.lifecycle.ViewModel() {

    private val _uiState = kotlinx.coroutines.flow.MutableStateFlow(ProfileUiState())
    val uiState: kotlinx.coroutines.flow.StateFlow<ProfileUiState> = _uiState

    fun loadUserInfo() {
        kotlinx.coroutines.viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            val result = userRepository.getUserInfo()
            result.onSuccess { userInfo ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    userInfo = userInfo
                )
            }.onFailure { exception ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    userInfo = null
                )
            }
        }
    }
}
