package com.example.myapplication

import android.app.Application
import com.example.myapplication.data.AppDatabase

class FinanceApplication : Application() {
    // Создаем базу данных один раз при запуске приложения
    val database by lazy { AppDatabase.getDatabase(this) }
}