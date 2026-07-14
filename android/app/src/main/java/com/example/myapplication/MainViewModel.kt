package com.example.myapplication

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.AppRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.time.LocalDate

class MainViewModel(private val repository: AppRepository) : ViewModel() {

    // При старте пробуем синхронизироваться (фоном)
    init {
        viewModelScope.launch {
            repository.syncExpenses()
        }
    }

    // --- ДАННЫЕ UI ---
    val uiState: StateFlow<List<DayData>> = repository.allExpenses
        .map { entities ->
            val grouped = entities.groupBy { it.date }
            grouped.map { (date, list) ->
                DayData(
                    date = date,
                    expenses = list.map { entity ->
                        ExpenseModel(
                            id = entity.id.toString(),
                            title = entity.title,
                            amount = entity.amount,
                            category = entity.category
                        )
                    }
                )
            }.sortedBy { LocalDate.parse(it.date) }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val smsSendersState: StateFlow<List<String>> = repository.smsSenders
        .map { list -> list.map { it.senderId } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())


    // --- ДЕЙСТВИЯ ---

    fun addExpense(title: String, amount: Double, category: String, date: String) {
        viewModelScope.launch {
            repository.insertExpense(title, amount, category, date)
        }
    }

    fun deleteExpense(idString: String) {
        viewModelScope.launch {
            idString.toLongOrNull()?.let { repository.deleteExpense(it) }
        }
    }

    // --- АВТОРИЗАЦИЯ (Новое) ---

    fun login(email: String, pass: String, onSuccess: () -> Unit, onError: () -> Unit) {
        viewModelScope.launch {
            val success = repository.login(email, pass)
            if (success) onSuccess() else onError()
        }
    }

    fun register(email: String, pass: String, name: String, onSuccess: () -> Unit, onError: () -> Unit) {
        viewModelScope.launch {
            val success = repository.register(email, pass, name)
            if (success) {
                // Если зарегистрировались, сразу пробуем войти
                login(email, pass, onSuccess, onError)
            } else {
                onError()
            }
        }
    }

    fun logout(onLogoutComplete: () -> Unit) {
        viewModelScope.launch {
            repository.logout()
            onLogoutComplete()
        }
    }

    // --- НАСТРОЙКИ СМС ---
    fun addSmsNumber(number: String) {
        viewModelScope.launch { if (number.isNotBlank()) repository.addSmsSender(number.trim()) }
    }
    fun deleteSmsNumber(number: String) {
        viewModelScope.launch { repository.deleteSmsSender(number) }
    }
}

class MainViewModelFactory(private val repository: AppRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return MainViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}