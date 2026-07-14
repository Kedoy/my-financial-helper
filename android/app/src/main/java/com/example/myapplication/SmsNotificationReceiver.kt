package com.example.myapplication


import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.example.myapplication.data.AppDatabase
import com.example.myapplication.data.ExpenseEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.time.LocalDate
import android.app.NotificationManager

class SmsNotificationReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action
        val notificationId = intent.getIntExtra("notification_id", 0)

        // Закрываем уведомление, так как пользователь нажал кнопку
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.cancel(notificationId)

        if (action == "ACTION_ADD_EXPENSE") {
            val amount = intent.getDoubleExtra("amount", 0.0)

            // Если сумма валидная, добавляем в расходы
            if (amount > 0) {
                val db = AppDatabase.getDatabase(context)
                val dao = db.appDao()

                // Запускаем корутину (т.к. БД работает асинхронно)
                CoroutineScope(Dispatchers.IO).launch {
                    dao.insertExpense(
                        ExpenseEntity(
                            title = "Из СМС",
                            amount = amount,
                            category = "Другое", // Как ты и просил
                            date = LocalDate.now().toString()
                        )
                    )
                }
            }
        }
        // Если action == "ACTION_LATER", мы просто закрыли уведомление (оно уже сохранено в истории СМС в SmsReceiver)
    }
}