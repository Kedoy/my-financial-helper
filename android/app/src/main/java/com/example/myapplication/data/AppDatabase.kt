package com.example.myapplication.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

// Перечисляем все наши таблицы и версию базы
@Database(
    entities = [ExpenseEntity::class, SmsSenderEntity::class, UserSettingsEntity::class, SmsTransactionEntity::class], // <-- Добавили сюда
    version = 2,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    // Ссылка на DAO
    abstract fun appDao(): AppDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        // Стандартный код для создания базы данных (Singleton)
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "finance_app_database" // Имя файла базы на телефоне
                )
                    // Разрушительная миграция (если поменяем структуру, старые данные удалятся)
                    // Для учебного проекта это ОК, для продакшена - нет.
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}