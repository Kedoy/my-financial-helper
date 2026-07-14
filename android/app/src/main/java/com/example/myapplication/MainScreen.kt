package com.example.myapplication

import androidx.compose.animation.*
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Assessment
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import java.time.LocalDate

// --- ЦВЕТА ---
val AppBackground = Color(0xFF1A1A1A)
val CardBackground = Color(0xFF121212)
val CardBorder = Color(0xFF2B2B2B)
val PrimaryBlue = Color(0xFF1F6FEB)
val AccentBlue = Color(0xFF4A90E2)
val TextPrimary = Color(0xFFE6E6E6)
val TextSecondary = Color(0xFF9AA4B2)
val CategoryBg = Color(0xFF1B1B1B)
val CategoryBgExpanded = Color(0xFF1F1F1F)
val DialogBg = Color(0xFF222222)
val DeleteRed = Color(0xFFFF5252)

val sampleCategories = listOf("Еда", "Дом", "Транспорт", "Развлечения", "Другое")

// --- ЭКРАН ---
@OptIn(ExperimentalFoundationApi::class, ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    viewModel: MainViewModel,
    onNavigateToAnalytics: () -> Unit,
    onNavigateToSettings: () -> Unit
) {
    val scope = rememberCoroutineScope()

    // 1. Дни из Базы Данных
    val dbDays by viewModel.uiState.collectAsState()

    // 2. Локальные дни (пустые)
    val localDays = remember { mutableStateListOf<DayData>() }

    // --- ИСПРАВЛЕНИЕ БАГА ТУТ ---
    // Мы берем локальные дни, но ВЫКИДЫВАЕМ из них те даты, которые уже есть в БД.
    // Таким образом, пустая карточка заменяется заполненной из базы.
    val allDays = remember(dbDays, localDays.toList()) {
        val dbDates = dbDays.map { it.date }.toSet()
        // Оставляем только те локальные дни, которых НЕТ в базе
        val uniqueLocalDays = localDays.filter { it.date !in dbDates }

        (dbDays + uniqueLocalDays).sortedBy { LocalDate.parse(it.date) }
    }.ifEmpty {
        listOf(DayData(LocalDate.now().toString(), emptyList()))
    }
    // ----------------------------

    val pagerState = rememberPagerState(pageCount = { allDays.size })

    // Автопрокрутка к последнему дню при старте
    LaunchedEffect(Unit) {
        if (allDays.isNotEmpty()) {
            pagerState.scrollToPage(allDays.size - 1)
        }
    }

    var showAddDialog by remember { mutableStateOf(false) }
    var selectedCategoryForAdd by remember { mutableStateOf("") }

    Scaffold(
        containerColor = AppBackground,
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Учёт расходов", color = TextPrimary, fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = AppBackground),
                navigationIcon = {
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings", tint = TextPrimary)
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToAnalytics) {
                        Icon(Icons.Default.Assessment, contentDescription = "Analytics", tint = PrimaryBlue)
                    }

                    TextButton(onClick = {
                        val lastDateStr = allDays.last().date
                        val nextDate = LocalDate.parse(lastDateStr).plusDays(1).toString()

                        // Добавляем пустой день
                        localDays.add(DayData(nextDate, emptyList()))

                        // Скроллим к новому дню
                        scope.launch {
                            // Небольшая задержка, чтобы UI успел обновиться
                            kotlinx.coroutines.delay(100)
                            pagerState.animateScrollToPage(allDays.size)
                        }
                    }) {
                        Text("+ День", color = PrimaryBlue, fontWeight = FontWeight.Bold)
                    }
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).fillMaxSize()) {
            HorizontalPager(
                state = pagerState,
                contentPadding = PaddingValues(horizontal = 24.dp),
                pageSpacing = 16.dp,
                modifier = Modifier.weight(1f).padding(top = 16.dp)
            ) { page ->
                val dayData = allDays.getOrNull(page)

                if (dayData != null) {
                    DayCard(
                        dayData = dayData,
                        onAddExpenseClick = { cat ->
                            selectedCategoryForAdd = cat
                            showAddDialog = true
                        },
                        onDeleteExpense = { expense ->
                            viewModel.deleteExpense(expense.id)
                        }
                    )
                }
            }

            // Точки-индикаторы
            Row(
                Modifier.wrapContentHeight().fillMaxWidth().padding(vertical = 16.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                repeat(pagerState.pageCount) { iteration ->
                    val color = if (pagerState.currentPage == iteration) PrimaryBlue else Color.DarkGray
                    Box(modifier = Modifier.padding(2.dp).clip(CircleShape).background(color).size(8.dp))
                }
            }
        }
    }

    if (showAddDialog) {
        AddExpenseDialog(
            initialCategory = selectedCategoryForAdd,
            onDismiss = { showAddDialog = false },
            onSave = { title, amount, category ->
                val currentDayDate = allDays[pagerState.currentPage].date

                viewModel.addExpense(
                    title = title,
                    amount = amount,
                    category = category,
                    date = currentDayDate
                )
                showAddDialog = false
            }
        )
    }
}

// --- ВСПОМОГАТЕЛЬНЫЕ КОМПОНЕНТЫ ---

@Composable
fun DayCard(
    dayData: DayData,
    onAddExpenseClick: (String) -> Unit,
    onDeleteExpense: (ExpenseModel) -> Unit
) {
    val dayTotal = dayData.expenses.sumOf { it.amount }
    val grouped = dayData.expenses.groupBy { it.category }

    Card(
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder),
        modifier = Modifier.fillMaxHeight(0.95f).fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = dayData.date, color = TextPrimary, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                if (dayTotal > 0) {
                    Text(
                        text = "${dayTotal.toInt()} ₽",
                        color = AccentBlue,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        modifier = Modifier.background(Color(0x224A90E2), RoundedCornerShape(8.dp)).padding(horizontal = 10.dp, vertical = 5.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.weight(1f)) {
                items(sampleCategories) { category ->
                    val expensesInCategory = grouped[category] ?: emptyList()
                    CategoryRow(
                        category = category,
                        expenses = expensesInCategory,
                        onAddClick = { onAddExpenseClick(category) },
                        onDeleteExpense = onDeleteExpense
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))
            Button(
                onClick = { onAddExpenseClick(sampleCategories.first()) },
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth().height(50.dp)
            ) {
                Text("+ Добавить расход", color = Color.White, fontSize = 16.sp)
            }
        }
    }
}

@Composable
fun CategoryRow(
    category: String,
    expenses: List<ExpenseModel>,
    onAddClick: () -> Unit,
    onDeleteExpense: (ExpenseModel) -> Unit
) {
    var isExpanded by remember { mutableStateOf(expenses.isNotEmpty()) }
    // Автораскрытие если появились расходы
    LaunchedEffect(expenses.size) {
        if (expenses.isNotEmpty()) isExpanded = true
    }

    val categoryTotal = expenses.sumOf { it.amount }
    val bgColor = if (isExpanded) CategoryBgExpanded else CategoryBg

    Column(
        modifier = Modifier
            .border(1.dp, if (isExpanded) Color(0xFF2F2F2F) else Color(0xFF252525), RoundedCornerShape(8.dp))
            .background(bgColor, RoundedCornerShape(8.dp))
            .clip(RoundedCornerShape(8.dp))
    ) {
        Row(
            modifier = Modifier.clickable { isExpanded = !isExpanded }.padding(12.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(text = category, color = TextPrimary, fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
                if (categoryTotal > 0) {
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        text = "${categoryTotal.toInt()} ₽",
                        color = TextSecondary,
                        fontSize = 13.sp,
                        modifier = Modifier
                            .background(Color(0xFF2A2A2A), RoundedCornerShape(4.dp))
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = { onAddClick() }, modifier = Modifier.size(28.dp)) {
                    Icon(Icons.Default.Add, "Add", tint = TextSecondary)
                }
                Icon(
                    imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = null,
                    tint = if (isExpanded) PrimaryBlue else Color.Gray,
                    modifier = Modifier.padding(start = 4.dp)
                )
            }
        }

        AnimatedVisibility(visible = isExpanded) {
            Column {
                expenses.forEach { expense ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 12.dp, vertical = 4.dp)
                            .background(Color(0xFF151515), RoundedCornerShape(6.dp))
                            .border(1.dp, Color(0xFF333333), RoundedCornerShape(6.dp))
                            .padding(10.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = expense.title, color = TextPrimary, fontSize = 14.sp, modifier = Modifier.weight(1f))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "${expense.amount.toInt()} ₽", color = AccentBlue, fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.width(12.dp))
                            Icon(
                                imageVector = Icons.Default.Close,
                                contentDescription = "Delete",
                                tint = DeleteRed,
                                modifier = Modifier.size(22.dp).clickable { onDeleteExpense(expense) }
                            )
                        }
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddExpenseDialog(
    initialCategory: String,
    onDismiss: () -> Unit,
    onSave: (String, Double, String) -> Unit
) {
    var title by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    var category by remember { mutableStateOf(initialCategory.ifEmpty { sampleCategories.first() }) }
    var expanded by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = DialogBg,
        title = { Text("Новый расход", color = TextPrimary) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                ExposedDropdownMenuBox(
                    expanded = expanded,
                    onExpandedChange = { expanded = !expanded }
                ) {
                    OutlinedTextField(
                        value = category,
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Категория") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary,
                            focusedBorderColor = PrimaryBlue,
                            unfocusedBorderColor = Color.Gray,
                            focusedLabelColor = PrimaryBlue,
                            unfocusedLabelColor = Color.Gray,
                            focusedContainerColor = Color(0xFF2A2A2A),
                            unfocusedContainerColor = Color(0xFF2A2A2A)
                        ),
                        modifier = Modifier.menuAnchor().fillMaxWidth()
                    )
                    ExposedDropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false },
                        modifier = Modifier.background(Color(0xFF2A2A2A))
                    ) {
                        sampleCategories.forEach { item ->
                            DropdownMenuItem(
                                text = { Text(text = item, color = TextPrimary) },
                                onClick = {
                                    category = item
                                    expanded = false
                                },
                                contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding
                            )
                        }
                    }
                }
                OutlinedTextField(
                    value = title,
                    onValueChange = { title = it },
                    label = { Text("Название") },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary, focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color.Gray, focusedLabelColor = PrimaryBlue, unfocusedLabelColor = Color.Gray),
                    modifier = Modifier.fillMaxWidth()
                )
                OutlinedTextField(
                    value = amount,
                    onValueChange = { amount = it },
                    label = { Text("Сумма") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    colors = OutlinedTextFieldDefaults.colors(focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary, focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color.Gray, focusedLabelColor = PrimaryBlue, unfocusedLabelColor = Color.Gray),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { if (title.isNotEmpty() && amount.isNotEmpty()) onSave(title, amount.toDoubleOrNull() ?: 0.0, category) },
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
            ) { Text("Сохранить", color = Color.White) }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Отмена", color = TextSecondary) } }
    )
}