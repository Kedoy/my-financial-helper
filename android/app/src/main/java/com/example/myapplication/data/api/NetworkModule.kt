package com.example.myapplication.data.api

import com.example.myapplication.data.AppDao
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object NetworkModule {

    private const val BASE_URL = "http://185.255.132.251:8000"

    // Создаем клиент с нуля
    fun provideApi(dao: AppDao): FinanceApi {
        // 1. Логгер (чтобы видеть запросы в Logcat)
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        // 2. Перехватчик для добавления Токена
        val authInterceptor = Interceptor { chain ->
            val originalRequest = chain.request()

            // Исключаем эндпоинты авторизации из проверки токена
            if (originalRequest.url.encodedPath.contains("/auth/")) {
                return@Interceptor chain.proceed(originalRequest)
            }

            // Достаем токен из БД синхронно (так как Interceptor работает в потоке сети)
            // В реальном проекте лучше хранить токен в EncryptedSharedPreferences,
            // но для учебного возьмем из нашей UserSettings таблицы.
            val token = runBlocking {
                dao.getUserSettings()?.token
            }

            val newRequest = if (!token.isNullOrEmpty()) {
                originalRequest.newBuilder()
                    .header("Authorization", "Bearer $token")
                    .build()
            } else {
                originalRequest
            }
            chain.proceed(newRequest)
        }

        // 3. Сборка OkHttp
        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor(authInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

        // 4. Сборка Retrofit
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(FinanceApi::class.java)
    }
}