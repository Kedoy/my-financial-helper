package com.example.myapplication

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.provider.Telephony
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.example.myapplication.data.AppDatabase
import com.example.myapplication.data.SmsTransactionEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.regex.Pattern

class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {

            // Получаем сообщения
            val msgs = Telephony.Sms.Intents.getMessagesFromIntent(intent)

            // Получаем базу данных
            val db = AppDatabase.getDatabase(context)
            val dao = db.appDao()

            // Используем goAsync, чтобы Receiver не "умер" пока мы лезем в базу
            val pendingResult = goAsync()

            CoroutineScope(Dispatchers.IO).launch {
                try {
                    // 1. Получаем список отслеживаемых номеров
                    val trackedNumbers = dao.getSmsSendersSync()
                    val trackedSet = trackedNumbers.map { it.senderId.lowercase() }.toSet()

                    msgs?.forEach { sms ->
                        val sender = sms.originatingAddress?.lowercase() ?: ""
                        val body = sms.messageBody ?: ""

                        // 2. Проверяем, отслеживаем ли мы этот номер
                        // (Сравниваем, содержится ли sender в списке, или список содержит sender)
                        val isTracked = trackedSet.any { tracked ->
                            sender.contains(tracked) || tracked.contains(sender)
                        }

                        if (isTracked) {
                            // 3. Ищем сумму регулярным выражением
                            val amount = extractAmount(body)

                            if (amount != null) {
                                // 4. Сохраняем в историю СМС (пункт "Потом")
                                dao.insertSms(
                                    SmsTransactionEntity(
                                        sender = sms.originatingAddress ?: "Unknown",
                                        messageBody = body,
                                        parsedAmount = amount,
                                        date = LocalDateTime.now().toString(),
                                        isProcessed = false
                                    )
                                )

                                // 5. Показываем интерактивное уведомление
                                showNotification(context, amount, sms.originatingAddress ?: "Bank")
                            }
                        }
                    }
                } finally {
                    pendingResult.finish()
                }
            }
        }
    }

    // Регулярное выражение для поиска суммы (ищет "150.00", "150", "1 200.50")
    private fun extractAmount(text: String): Double? {
        // Паттерн ищет число, возможно с пробелами между тысячами, и возможно с копейками
        // Пример работы: "Покупка 1500р" -> 1500.0; "Списание 240.50 RUB" -> 240.50
        val regex = "\\b\\d+[\\d\\s]*([.,]\\d{1,2})?"
        val pattern = Pattern.compile(regex)
        val matcher = pattern.matcher(text)

        if (matcher.find()) {
            // Убираем пробелы и меняем запятую на точку
            val rawString = matcher.group().replace(" ", "").replace(",", ".")
            return rawString.toDoubleOrNull()
        }
        return null
    }

    private fun showNotification(context: Context, amount: Double, sender: String) {
        // Проверка разрешения на уведомления (Android 13+)
        if (Build.VERSION.SDK_INT >=33) {
            if (ActivityCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                return
            }
        }

        val channelId = "finance_sms_channel"
        val notificationId = (System.currentTimeMillis() % 10000).toInt()

        createNotificationChannel(context, channelId)

        // Интент для кнопки "Добавить"
        val addIntent = Intent(context, SmsNotificationReceiver::class.java).apply {
            action = "ACTION_ADD_EXPENSE"
            putExtra("amount", amount)
            putExtra("notification_id", notificationId)
        }
        val addPendingIntent = PendingIntent.getBroadcast(
            context, notificationId, addIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // Интент для кнопки "Потом" (Просто закрыть)
        val laterIntent = Intent(context, SmsNotificationReceiver::class.java).apply {
            action = "ACTION_LATER"
            putExtra("notification_id", notificationId)
        }
        val laterPendingIntent = PendingIntent.getBroadcast(
            context, notificationId + 1, laterIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info) // Замени на свою иконку, если есть
            .setContentTitle("Новая трата: $sender")
            .setContentText("Вы потратили $amount ₽. Добавить в расходы?")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .addAction(android.R.drawable.ic_menu_add, "Добавить", addPendingIntent) // Кнопка 1
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Потом", laterPendingIntent) // Кнопка 2

        NotificationManagerCompat.from(context).notify(notificationId, builder.build())
    }

    private fun createNotificationChannel(context: Context, channelId: String) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Sms Tracker"
            val descriptionText = "Уведомления о тратах из СМС"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(channelId, name, importance).apply {
                description = descriptionText
            }
            val notificationManager: NotificationManager =
                context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
}