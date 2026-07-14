package com.example.myapplication

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.math.roundToInt

// ЦВЕТА
private val BgColor = Color(0xFF1A1A1A)
private val CardBg = Color(0xFF121212)
private val Primary = Color(0xFF1F6FEB)
private val TextWhite = Color(0xFFE6E6E6)
private val TextGray = Color(0xFF9AA4B2)

// Цвета для графиков
private val ChartColors = listOf(
    Color(0xFF4A90E2), // Голубой
    Color(0xFF50E3C2), // Бирюзовый
    Color(0xFFF5A623), // Оранжевый
    Color(0xFFE04F5F), // Красный
    Color(0xFF9013FE), // Фиолетовый
    Color(0xFFB8E986)  // Салатовый
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyticsScreen(
    viewModel: MainViewModel,]
    onBack: () -> Unit
) {
    // Получаем данные из базы (автоматически обновляются)
    val allDays by viewModel.uiState.collectAsState()

    // Переключатель Неделя/Месяц
    var selectedPeriod by remember { mutableStateOf("Неделя") }

    // --- ПОДГОТОВКА ДАННЫХ ---

    // 1. Фильтруем расходы по выбранному периоду
    val relevantExpenses = remember(allDays, selectedPeriod) {
        val daysCount = if (selectedPeriod == "Неделя") 7L else 30L
        val startDate = LocalDate.now().minusDays(daysCount - 1) // -1 чтобы включить сегодня

        // Собираем все расходы в плоский список, если дата подходит
        allDays.filter {
            val dayDate = LocalDate.parse(it.date)
            !dayDate.isBefore(startDate) && !dayDate.isAfter(LocalDate.now())
        }.flatMap { day ->
            day.expenses.map { expense -> expense to day.date }
        }
    }

    // 2. Данные для Круговой диаграммы (Группировка по категориям)
    val categoryStats = remember(relevantExpenses) {
        relevantExpenses.groupBy { it.first.category }
            .mapValues { entry -> entry.value.sumOf { it.first.amount } }
            .toList()
            .sortedByDescending { it.second } // Сортируем от большего к меньшему
    }

    val totalSum = categoryStats.sumOf { it.second }

    // 3. Данные для Столбчатой диаграммы (Группировка по датам)
    val dailyStats = remember(relevantExpenses, selectedPeriod) {
        val daysCount = if (selectedPeriod == "Неделя") 7 else 30
        val map = relevantExpenses.groupBy { it.second }
            .mapValues { entry -> entry.value.sumOf { it.first.amount } }

        // Создаем список за последние N дней, заполняя нулями пустые дни
        List(daysCount) { i ->
            val date = LocalDate.now().minusDays((daysCount - 1 - i).toLong())
            val dateStr = date.toString()
            val amount = map[dateStr] ?: 0.0
            date to amount
        }
    }

    Scaffold(
        containerColor = BgColor,
        topBar = {
            TopAppBar(
                title = { Text("Аналитика", color = TextWhite, fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextWhite)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = BgColor)
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            // 1. Переключатель
            item {
                PeriodSelector(
                    selected = selectedPeriod,
                    onSelect = { selectedPeriod = it }
                )
            }

            // 2. Круговая диаграмма
            item {
                ChartCard(title = "По категориям") {
                    if (totalSum > 0) {
                        PieChartActual(categoryStats, totalSum)
                    } else {
                        Text("Нет данных за этот период", color = TextGray, modifier = Modifier.padding(10.dp))
                    }
                }
            }

            // 3. Столбчатая диаграмма
            item {
                ChartCard(title = "Динамика ($selectedPeriod)") {
                    if (totalSum > 0) {
                        BarChartActual(dailyStats)
                    } else {
                        Text("Нет расходов", color = TextGray, modifier = Modifier.padding(10.dp))
                    }
                }
            }
        }
    }
}

// --- ВИЗУАЛИЗАЦИЯ (LOGIC) ---

@Composable
fun PieChartActual(
    data: List<Pair<String, Double>>, // Категория -> Сумма
    total: Double
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        // КРУГ
        Box(modifier = Modifier.size(160.dp)) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val strokeWidth = 35.dp.toPx()
                var startAngle = -90f

                data.forEachIndexed { index, pair ->
                    val percentage = (pair.second / total).toFloat()
                    val sweepAngle = 360f * percentage

                    drawArc(
                        color = ChartColors[index % ChartColors.size],
                        startAngle = startAngle,
                        sweepAngle = sweepAngle - 2f, // Отступ
                        useCenter = false,
                        style = Stroke(width = strokeWidth)
                    )
                    startAngle += sweepAngle
                }
            }
            // Текст в центре
            Column(
                modifier = Modifier.align(Alignment.Center),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("Всего", color = TextGray, fontSize = 12.sp)
                Text(
                    text = "${total.toInt()}",
                    color = TextWhite,
                    fontWeight = FontWeight.Bold,
                    fontSize = 18.sp
                )
            }
        }

        Spacer(modifier = Modifier.width(24.dp))


        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            data.forEachIndexed { index, pair ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    // Цветной кружок
                    Box(modifier = Modifier.size(10.dp).background(ChartColors[index % ChartColors.size], CircleShape))
                    Spacer(modifier = Modifier.width(8.dp))

                    // Название и процент
                    Column {
                        Text(pair.first, color = TextWhite, fontSize = 14.sp)
                        val percent = ((pair.second / total) * 100).toInt()
                        Text("$percent% (${pair.second.toInt()} ₽)", color = TextGray, fontSize = 12.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun BarChartActual(
    data: List<Pair<LocalDate, Double>> // Дата -> Сумма
) {
    val maxAmount = data.maxOfOrNull { it.second } ?: 1.0
    // Если макс. сумма 0, ставим 1, чтобы не делить на ноль
    val safeMax = if (maxAmount == 0.0) 1.0 else maxAmount

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(160.dp), // Высота графика
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.Bottom
    ) {
        data.forEach { (date, amount) ->
            // Вычисляем высоту столбца (от 0.0 до 1.0)
            val barHeightFraction = (amount / safeMax).toFloat()
            // Минимальная высота, чтобы столбик было видно, даже если сумма маленькая
            val actualHeight = if (amount > 0 && barHeightFraction < 0.05f) 0.05f else barHeightFraction

            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.weight(1f) // Равномерная ширина
            ) {
                // Сам столбик
                Box(
                    modifier = Modifier
                        .fillMaxHeight(actualHeight)
                        .fillMaxWidth(0.7f) // Ширина столбика относительно места
                        .background(
                            if (amount > 0) Primary else Color(0xFF2A2A2A),
                            RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp)
                        )
                )

                Spacer(modifier = Modifier.height(6.dp))

                // Подпись (день месяца)
                Text(
                    text = date.format(DateTimeFormatter.ofPattern("dd")), // Только число, например "15"
                    color = if (date == LocalDate.now()) TextWhite else TextGray,
                    fontSize = 10.sp,
                    fontWeight = if (date == LocalDate.now()) FontWeight.Bold else FontWeight.Normal
                )
            }
        }
    }
}

// --- ВСПОМОГАТЕЛЬНЫЕ КОМПОНЕНТЫ ---

@Composable
fun PeriodSelector(selected: String, onSelect: (String) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardBg, RoundedCornerShape(10.dp))
            .border(1.dp, Color(0xFF2B2B2B), RoundedCornerShape(10.dp))
            .padding(4.dp)
    ) {
        listOf("Неделя", "Месяц").forEach { period ->
            val isSelected = selected == period
            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(8.dp))
                    .background(if (isSelected) Primary else Color.Transparent)
                    .clickable { onSelect(period) }
                    .padding(vertical = 10.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = period,
                    color = if (isSelected) TextWhite else TextGray,
                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                )
            }
        }
    }
}

@Composable
fun ChartCard(title: String, content: @Composable () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF2B2B2B)),
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(title, color = TextWhite, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(20.dp))
            content()
        }
    }
}