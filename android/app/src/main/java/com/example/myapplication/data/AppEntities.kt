package com.example.myapplication.data

import androidx.room.Entity
import androidx.room.PrimaryKey

// 1. Таблица Расходов
@Entity(tableName = "expenses")
data class ExpenseEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,       // Локальный ID (для телефона)

    val title: String,
    val amount: Double,
    val category: String,
    val date: String,

    // --- НОВЫЕ ПОЛЯ ДЛЯ СИНХРОНИЗАЦИИ ---
    val remoteId: Int? = null,  // ID на сервере (может быть null, если еще не отправили)
    val isSynced: Boolean = false, // false = надо отправить на сервер
    val isDeleted: Boolean = false // (На будущее) для "мягкого" удаления
)

// 2. Таблица для СМС-парсинга (номера банков)
@Entity(tableName = "sms_senders")
data class SmsSenderEntity(
    @PrimaryKey
    val senderId: String // Номер или имя, например "900" или "Tinkoff"
)

// 3. Таблица настроек пользователя (Авторизация)
// Мы будем хранить здесь всего одну строку с id=1
@Entity(tableName = "user_settings")
data class UserSettingsEntity(
    @PrimaryKey
    val id: Int = 1, // Всегда 1, чтобы перезаписывать одну и ту же строку

    val isLoggedIn: Boolean = false, // Вошел ли юзер
    val username: String? = null,    // Логин
    val token: String? = null        // Токен авторизации (для API)
)

// 4. История СМС (Таблица для хранения пойманных уведомлений)
@Entity(tableName = "sms_history")
data class SmsTransactionEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val sender: String,       // От кого (900, Tinkoff)
    val messageBody: String,  // Текст сообщения
    val parsedAmount: Double, // Сумма, которую мы вытащили
    val date: String,         // Дата получения
    val isProcessed: Boolean = false // false = "Потом", true = "Добавлено в расходы"
)