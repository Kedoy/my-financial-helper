package com.example.myapplication


import java.util.UUID

// Модель одной траты для UI
data class ExpenseModel(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val amount: Double,
    val category: String
)

// Модель дня для UI
data class DayData(
    val date: String,
    val expenses: List<ExpenseModel>
)