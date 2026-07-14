package com.example.myapplication


import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.Message
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// ЦВЕТА
private val BgColor = Color(0xFF1A1A1A)
private val CardBg = Color(0xFF121212)
private val Primary = Color(0xFF1F6FEB)
private val TextWhite = Color(0xFFE6E6E6)
private val TextGray = Color(0xFF9AA4B2)


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: MainViewModel,
    onBack: () -> Unit,
    onLogout: () -> Unit
) {
    // Подписываемся на список номеров из БД
    val smsNumbers by viewModel.smsSendersState.collectAsState()

    // Поле ввода нового номера
    var newNumber by remember { mutableStateOf("") }

    Scaffold(
        containerColor = BgColor,
        topBar = {
            TopAppBar(
                title = { Text("Настройки", color = TextWhite, fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextWhite)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = BgColor)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // --- БЛОК 1: СМС ПАРСИНГ ---
            Text(
                "Источники СМС (Банки)",
                color = Primary,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            // Поле ввода + Кнопка
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = newNumber,
                    onValueChange = { newNumber = it },
                    label = { Text("Номер или Имя (напр. 900)") },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextWhite,
                        unfocusedTextColor = TextWhite,
                        focusedBorderColor = Primary,
                        unfocusedBorderColor = TextGray,
                        focusedLabelColor = Primary,
                        unfocusedLabelColor = TextGray,
                        focusedContainerColor = CardBg,
                        unfocusedContainerColor = CardBg
                    ),
                    modifier = Modifier.weight(1f),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = {
                        if (newNumber.isNotBlank()) {
                            viewModel.addSmsNumber(newNumber)
                            newNumber = ""
                        }
                    })
                )

                // Кнопка Добавить (Квадратная)
                Button(
                    onClick = {
                        if (newNumber.isNotBlank()) {
                            viewModel.addSmsNumber(newNumber)
                            newNumber = ""
                        }
                    },
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Primary),
                    modifier = Modifier.height(56.dp).width(56.dp),
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Add", tint = Color.White)
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Список добавленных номеров
            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(smsNumbers) { number ->
                    SmsNumberCard(
                        number = number,
                        onDelete = { viewModel.deleteSmsNumber(number) }
                    )
                }

                if (smsNumbers.isEmpty()) {
                    item {
                        Text(
                            "Список пуст. Добавьте номера, от которых приходят СМС о списаниях.",
                            color = TextGray,
                            fontSize = 14.sp,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // --- БЛОК 2: АККАУНТ ---
            HorizontalDivider(color = Color(0xFF333333))
            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = {
                    viewModel.logout {
                        onLogout()
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = DeleteRed.copy(alpha = 0.1f)),
                shape = RoundedCornerShape(12.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, DeleteRed),
                modifier = Modifier.fillMaxWidth().height(50.dp)
            ) {
                Icon(Icons.Default.ExitToApp, contentDescription = null, tint = DeleteRed)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Выйти из аккаунта", color = DeleteRed, fontWeight = FontWeight.Bold)
            }
        }
    }
}

// Карточка номера (Стиль как у расходов)
@Composable
fun SmsNumberCard(number: String, onDelete: () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF2B2B2B)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Иконка сообщения
                Icon(Icons.Default.Message, contentDescription = null, tint = Primary)
                Spacer(modifier = Modifier.width(16.dp))
                // Номер
                Text(
                    text = number,
                    color = TextWhite,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // Кнопка удаления
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Close, contentDescription = "Delete", tint = DeleteRed)
            }
        }
    }
}