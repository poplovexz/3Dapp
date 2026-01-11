package com.anglephoto.app.ui.auth

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.anglephoto.app.data.repository.UserRepository

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    viewModel: LoginViewModel = hiltViewModel()
) {
    var identifier by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoginMode by remember { mutableStateOf(true) }
    var code by remember { mutableStateOf("") }
    var newPassword by remember { mutableStateOf("") }
    var showCodeInput by remember { mutableStateOf(false) }

    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(uiState.isLoggedIn) {
        if (uiState.isLoggedIn) {
            onLoginSuccess()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "角度拍摄",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "AI 多角度照片生成",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f)
        )

        Spacer(modifier = Modifier.height(48.dp))

        if (showCodeInput) {
            OutlinedTextField(
                value = code,
                onValueChange = { code = it },
                label = { Text("验证码") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                isError = uiState.errorMessage?.contains("验证码") == true
            )
            
            OutlinedTextField(
                value = newPassword,
                onValueChange = { newPassword = it },
                label = { Text("新密码") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                isError = uiState.errorMessage?.contains("密码") == true
            )
        } else {
            OutlinedTextField(
                value = identifier,
                onValueChange = { identifier = it },
                label = { Text(if (isLoginMode) "手机号/邮箱" else "手机号/邮箱") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("密码") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                isError = uiState.errorMessage?.contains("密码") == true
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (uiState.errorMessage != null) {
            Text(
                text = uiState.errorMessage ?: "",
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall
            )
            Spacer(modifier = Modifier.height(8.dp))
        }

        Button(
            onClick = {
                if (isLoginMode) {
                    viewModel.login(identifier, password)
                } else {
                    if (showCodeInput) {
                        viewModel.register(identifier, code, newPassword)
                    } else {
                        viewModel.sendCode(identifier)
                        showCodeInput = true
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = !uiState.isLoading && (
                if (showCodeInput) code.isNotBlank() && newPassword.isNotBlank() 
                else identifier.isNotBlank() && password.isNotBlank()
            )
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text(
                    text = when {
                        showCodeInput -> "注册"
                        isLoginMode -> "登录"
                        else -> "发送验证码"
                    },
                    style = MaterialTheme.typography.titleMedium
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = {
                isLoginMode = !isLoginMode
                showCodeInput = false
                viewModel.clearError()
            }
        ) {
            Text(
                text = if (isLoginMode) "还没有账号？立即注册" else "已有账号？立即登录"
            )
        }

        if (showCodeInput) {
            TextButton(
                onClick = {
                    showCodeInput = false
                    viewModel.clearError()
                }
            ) {
                Text("重新输入手机号/邮箱")
            }
        }
    }
}
