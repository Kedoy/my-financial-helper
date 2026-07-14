package com.example.myapplication

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.myapplication.data.AppRepository
// Поправил импорт, чтобы он соответствовал твоему пакету
import com.example.myapplication.data.api.NetworkModule

enum class AppScreen {
    LOGIN, MAIN, ANALYTICS, SETTINGS // Убрал REGISTER
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 1. База данных
        val database = (application as FinanceApplication).database

        // 2. API (СЕТЬ)
        val api = NetworkModule.provideApi(database.appDao())

        // 3. Репозиторий
        val repository = AppRepository(database.appDao(), api)

        val viewModelFactory = MainViewModelFactory(repository)

        setContent {
            MaterialTheme {
                Surface(modifier = androidx.compose.ui.Modifier.fillMaxSize()) {
                    var currentScreen by remember { mutableStateOf(AppScreen.LOGIN) }

                    // 4. Получаем ViewModel
                    val mainViewModel: MainViewModel = viewModel(factory = viewModelFactory)

                    when (currentScreen) {
                        AppScreen.LOGIN -> {
                            LoginScreen(
                                viewModel = mainViewModel, // Не забудь передать ViewModel!
                                onLoginSuccess = { currentScreen = AppScreen.MAIN }
                                // onNavigateToRegister убрали
                            )
                        }
                        // Блок REGISTER удален полностью

                        AppScreen.MAIN -> {
                            MainScreen(
                                viewModel = mainViewModel,
                                onNavigateToAnalytics = { currentScreen = AppScreen.ANALYTICS },
                                onNavigateToSettings = { currentScreen = AppScreen.SETTINGS }
                            )
                        }
                        AppScreen.ANALYTICS -> {
                            AnalyticsScreen(
                                viewModel = mainViewModel,
                                onBack = { currentScreen = AppScreen.MAIN }
                            )
                        }
                        AppScreen.SETTINGS -> {
                            SettingsScreen(
                                viewModel = mainViewModel,
                                onBack = { currentScreen = AppScreen.MAIN },
                                onLogout = {
                                    currentScreen = AppScreen.LOGIN
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}