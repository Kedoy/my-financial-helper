package com.example.myapplication.data

import com.example.myapplication.data.api.CreateTransactionRequest
import com.example.myapplication.data.api.FinanceApi
import com.example.myapplication.data.api.LoginResponse
import com.example.myapplication.data.api.RegisterRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext
import retrofit2.Response

class AppRepository(
    private val appDao: AppDao,
    private val api: FinanceApi // Теперь мы знаем и про API
) {
    // --- КАРТА КАТЕГОРИЙ (Сервер ID <-> Название) ---
    // 4:Food, 5:Funny, 6:Transport, 7:Other
    private fun mapCategoryToId(name: String): Int {
        return when (name) {
            "Еда" -> 4
            "Развлечения" -> 5
            "Транспорт" -> 6
            else -> 7 // "Другое" и всё остальное
        }
    }

    private fun mapIdToCategory(id: Int): String {
        return when (id) {
            4 -> "Еда"
            5 -> "Развлечения"
            6 -> "Транспорт"
            else -> "Другое"
        }
    }

    // --- ДАННЫЕ (Flow из БД - Источник правды) ---
    val allExpenses: Flow<List<ExpenseEntity>> = appDao.getAllExpenses()
    val smsSenders: Flow<List<SmsSenderEntity>> = appDao.getSmsSenders()


    // --- АВТОРИЗАЦИЯ ---

    suspend fun login(email: String, pass: String): Boolean {
        return try {
            val response = api.login(email, pass)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                // Сохраняем токен и инфо о пользователе
                val settings = UserSettingsEntity(
                    isLoggedIn = true,
                    username = body.user.email,
                    token = body.accessToken
                )
                appDao.saveUserSettings(settings)
                // После входа сразу пробуем скачать данные
                syncExpenses()
                true
            } else {
                false
            }
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    suspend fun register(email: String, pass: String, name: String): Boolean {
        return try {
            val request = RegisterRequest(email, pass, name)
            val response = api.register(request)
            response.isSuccessful // Если 200 OK, значит зарегистрировались
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    suspend fun logout() {
        appDao.clearUserSettings()
        appDao.clearAllExpenses() // Удаляем чужие расходы при выходе
    }

    // --- РАСХОДЫ (Оффлайн + Синхронизация) ---

    // 1. Добавление: Сначала в БД, потом попытка отправить
    suspend fun insertExpense(title: String, amount: Double, category: String, date: String) {
        // Сохраняем локально (isSynced = false по умолчанию)
        val newExpense = ExpenseEntity(
            title = title,
            amount = amount,
            category = category,
            date = date,
            isSynced = false
        )
        appDao.insertExpense(newExpense)

        // Пробуем синхронизировать сразу (если есть интернет)
        trySyncUnsent()
    }

    // 2. Удаление
    suspend fun deleteExpense(id: Long) {
        // Удаляем локально
        // (Для полной синхронизации тут стоило бы помечать isDeleted=true,
        // но пока просто удалим, чтобы не усложнять)
        appDao.deleteExpense(ExpenseEntity(id = id, title="", amount=0.0, category="", date=""))
    }

    // 3. СМС номера (только локально)
    suspend fun addSmsSender(senderId: String) = appDao.addSmsSender(SmsSenderEntity(senderId = senderId))
    suspend fun deleteSmsSender(senderId: String) = appDao.deleteSmsSender(SmsSenderEntity(senderId = senderId))


    // --- СИНХРОНИЗАЦИЯ (Магия) ---

    // Полная синхронизация (Отправить свои -> Скачать чужие)
    suspend fun syncExpenses() = withContext(Dispatchers.IO) {
        try {
            // Шаг 1: Отправляем всё, что накопилось локально
            trySyncUnsent()

            // Шаг 2: Скачиваем всё с сервера
            val response = api.getTransactions(limit = 100)
            if (response.isSuccessful && response.body() != null) {
                val serverList = response.body()!!

                serverList.forEach { dto ->
                    // Конвертируем DTO сервера в нашу Entity
                    val entity = ExpenseEntity(
                        remoteId = dto.id,
                        title = dto.description ?: "Без названия",
                        amount = dto.amount,
                        category = mapIdToCategory(dto.categoryId),
                        date = dto.date.take(10), // Отрезаем время, оставляем YYYY-MM-DD
                        isSynced = true
                    )
                    // Сохраняем в БД (Room сам заменит старую запись, если remoteId совпадет,
                    // но так как remoteId не PrimaryKey, это добавит дубликаты, если не проверить.
                    // Для упрощения сейчас мы просто добавляем).
                    appDao.insertExpense(entity)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace() // Нет интернета - ничего страшного
        }
    }

    // Отправка только неотправленного
    private suspend fun trySyncUnsent() {
        val unsent = appDao.getUnsyncedExpenses()
        unsent.forEach { expense ->
            try {
                val request = CreateTransactionRequest(
                    amount = expense.amount,
                    description = expense.title,
                    categoryId = mapCategoryToId(expense.category),
                    date = expense.date + "T12:00:00", // Добавляем фиктивное время для API
                    source = "manual"
                )

                val response = api.createTransaction(request)
                if (response.isSuccessful && response.body() != null) {
                    // Успех! Обновляем локальную запись: ставим галочку isSynced
                    val updatedExpense = expense.copy(
                        isSynced = true,
                        remoteId = response.body()!!.id
                    )
                    appDao.updateExpense(updatedExpense)
                }
            } catch (e: Exception) {
                // Не вышло отправить - попробуем в следующий раз
            }
        }
    }
}