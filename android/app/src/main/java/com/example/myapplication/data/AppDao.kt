package com.example.myapplication.data

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface AppDao {
    // --- РАСХОДЫ ---
    @Query("SELECT * FROM expenses ORDER BY date DESC, id DESC")
    fun getAllExpenses(): Flow<List<ExpenseEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpense(expense: ExpenseEntity)

    @Delete
    suspend fun deleteExpense(expense: ExpenseEntity)

    // --- СМС ОТСЛЕЖИВАНИЕ (Обновили тут) ---
    // Теперь возвращает Flow, чтобы UI обновлялся сам
    @Query("SELECT * FROM sms_senders")
    fun getSmsSenders(): Flow<List<SmsSenderEntity>>

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun addSmsSender(sender: SmsSenderEntity)

    // Добавили удаление
    @Delete
    suspend fun deleteSmsSender(sender: SmsSenderEntity)

    // --- АВТОРИЗАЦИЯ ---
    @Query("SELECT * FROM user_settings WHERE id = 1")
    suspend fun getUserSettings(): UserSettingsEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveUserSettings(settings: UserSettingsEntity)

    // Полная очистка настроек (для выхода)
    @Query("DELETE FROM user_settings")
    suspend fun clearUserSettings()

    // --- ИСТОРИЯ СМС ---
    @Insert
    suspend fun insertSms(sms: SmsTransactionEntity)

    @Query("SELECT * FROM sms_history ORDER BY id DESC")
    fun getAllSmsHistory(): Flow<List<SmsTransactionEntity>>

    @Query("SELECT * FROM sms_senders")
    fun getSmsSendersSync(): List<SmsSenderEntity>

    // Получить расходы, которые еще не отправлены на сервер
    @Query("SELECT * FROM expenses WHERE isSynced = 0")
    suspend fun getUnsyncedExpenses(): List<ExpenseEntity>

    // Обновить конкретный расход (например, проставить ему remoteId после отправки)
    @androidx.room.Update
    suspend fun updateExpense(expense: ExpenseEntity)

    // Очистить все расходы (при выходе из аккаунта или полной синхронизации)
    @Query("DELETE FROM expenses")
    suspend fun clearAllExpenses()
}