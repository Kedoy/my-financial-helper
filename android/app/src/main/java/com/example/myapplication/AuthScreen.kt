package com.example.myapplication

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// Добавляем ViewModel в параметры
@Composable
fun LoginScreen(
    viewModel: MainViewModel,
    onLoginSuccess: () -> Unit,
    onNavigateToRegister: () -> Unit
) {
    var login by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) } // Индикатор загрузки
    var isError by remember { mutableStateOf(false) }

    AuthLayout(title = "Вход") {
        AuthTextField(value = login, onValueChange = { login = it }, label = "Email")
        Spacer(modifier = Modifier.height(16.dp))
        AuthPasswordField(value = password, onValueChange = { password = it }, label = "Пароль")

        if (isError) {
            Text("Ошибка входа. Проверьте данные.", color = ErrorRed, modifier = Modifier.padding(top=8.dp))
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                isLoading = true
                isError = false
                // ВЫЗЫВАЕМ РЕАЛЬНЫЙ LOGIN
                viewModel.login(
                    email = login,
                    pass = password,
                    onSuccess = {
                        isLoading = false
                        onLoginSuccess()
                    },
                    onError = {
                        isLoading = false
                        isError = true
                    }
                )
            },
            enabled = !isLoading, // Блокируем кнопку пока грузится
        ) {
            if (isLoading) {
                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            } else {
                Text("Войти", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun RegisterScreen(
    viewModel: MainViewModel,
    onRegisterSuccess: () -> Unit,
    onNavigateToLogin: () -> Unit
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    AuthLayout(title = "Регистрация") {
        AuthTextField(value = email, onValueChange = { email = it }, label = "Email")
        Spacer(modifier = Modifier.height(16.dp))
        AuthTextField(value = name, onValueChange = { name = it }, label = "Имя")
        Spacer(modifier = Modifier.height(16.dp))
        AuthPasswordField(value = password, onValueChange = { password = it }, label = "Пароль")

        if (errorMessage != null) {
            Text(errorMessage!!, color = ErrorRed, modifier = Modifier.padding(top=8.dp))
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                if (email.isBlank() || password.isBlank()) {
                    errorMessage = "Заполните все поля"
                } else {
                    isLoading = true
                    errorMessage = null
                    // ВЫЗЫВАЕМ РЕГИСТРАЦИЮ
                    viewModel.register(
                        email = email,
                        pass = password,
                        name = name,
                        onSuccess = {
                            isLoading = false
                            onRegisterSuccess()
                        },
                        onError = {
                            isLoading = false
                            errorMessage = "Ошибка регистрации"
                        }
                    )
                }
            },
            enabled = !isLoading,
        ) {
            if (isLoading) {
                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            } else {
                Text("Зарегистрироваться", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

private val ErrorRed = Color(0xFFCF6679)

// --- ЭКРАН ВХОДА ---
@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    onNavigateToRegister: () -> Unit
) {
    var login by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    AuthLayout(title = "Вход") {
        AuthTextField(
            value = login,
            onValueChange = { login = it },
            label = "Логин"
        )

        Spacer(modifier = Modifier.height(16.dp))

        AuthPasswordField(
            value = password,
            onValueChange = { password = it },
            label = "Пароль"
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Кнопка ВОЙТИ
        Button(
            onClick = onLoginSuccess, // Пока пускаем без проверки
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier.fillMaxWidth().height(50.dp)
        ) {
            Text("Войти", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Переход на регистрацию
        TextButton(onClick = onNavigateToRegister) {
            Text("Нет аккаунта? Зарегистрироваться", color = TextSecondary)
        }
    }
}

// --- ВСПОМОГАТЕЛЬНЫЕ КОМПОНЕНТЫ ---

@Composable
fun AuthLayout(title: String, content: @Composable ColumnScope.() -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(AppBackground),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                color = TextPrimary,
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 32.dp)
            )
            content()
        }
    }
}

@Composable
fun AuthTextField(value: String, onValueChange: (String) -> Unit, label: String) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = TextPrimary,
            unfocusedTextColor = TextPrimary,
            focusedContainerColor = CardBackground,
            unfocusedContainerColor = CardBackground,
            focusedBorderColor = PrimaryBlue,
            unfocusedBorderColor = Color(0xFF333333),
            focusedLabelColor = PrimaryBlue,
            unfocusedLabelColor = TextSecondary
        )
    )
}

@Composable
fun AuthPasswordField(value: String, onValueChange: (String) -> Unit, label: String) {
    var passwordVisible by remember { mutableStateOf(false) }

    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
        visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
        trailingIcon = {
            val image = if (passwordVisible) Icons.Filled.Visibility else Icons.Filled.VisibilityOff
            IconButton(onClick = { passwordVisible = !passwordVisible }) {
                Icon(imageVector = image, contentDescription = null, tint = TextSecondary)
            }
        },
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = TextPrimary,
            unfocusedTextColor = TextPrimary,
            focusedContainerColor = CardBackground,
            unfocusedContainerColor = CardBackground,
            focusedBorderColor = PrimaryBlue,
            unfocusedBorderColor = Color(0xFF333333),
            focusedLabelColor = PrimaryBlue,
            unfocusedLabelColor = TextSecondary
        )
    )
}