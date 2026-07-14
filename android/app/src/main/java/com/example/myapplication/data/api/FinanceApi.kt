package com.example.myapplication.data.api

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.*

// --- МОДЕЛИ ДАННЫХ (DTO) ---

// 1. Вход
data class LoginRequest(
    @SerializedName("username") val email: String, // Сервер ждет username, но это email
    @SerializedName("password") val password: String
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("user") val user: UserDto
)

// 2. Регистрация
data class RegisterRequest(
    val email: String,
    val password: String,
    @SerializedName("full_name") val fullName: String
)

data class UserDto(
    val id: Int,
    val email: String,
    @SerializedName("full_name") val fullName: String?
)

// 3. Транзакции (Расходы)
data class TransactionDto(
    val id: Int,
    val amount: Double,
    val description: String?,
    @SerializedName("category_id") val categoryId: Int,
    val date: String, // ISO формат "2026-01-16T10:30:00"
    val type: String = "expense"
)

// Тело для отправки новой транзакции (без ID)
data class CreateTransactionRequest(
    val amount: Double,
    val description: String,
    @SerializedName("category_id") val categoryId: Int,
    val date: String,
    val type: String = "expense",
    val source: String = "manual"
)

// --- ИНТЕРФЕЙС API ---

interface FinanceApi {

    // Авторизация
    @POST("/api/v1/auth/login")
    @FormUrlEncoded // Важно: сервер ждет x-www-form-urlencoded для логина
    suspend fun login(
        @Field("username") email: String,
        @Field("password") pass: String
    ): Response<LoginResponse>

    @POST("/api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<UserDto>

    // Получение расходов
    @GET("/api/v1/transactions/")
    suspend fun getTransactions(
        @Query("limit") limit: Int = 100,
        @Query("skip") skip: Int = 0
    ): Response<List<TransactionDto>>

    // Отправка расхода
    @POST("/api/v1/transactions/")
    suspend fun createTransaction(@Body request: CreateTransactionRequest): Response<TransactionDto>

    // Удаление
    @DELETE("/api/v1/transactions/{id}")
    suspend fun deleteTransaction(@Path("id") id: Int): Response<Unit>
}