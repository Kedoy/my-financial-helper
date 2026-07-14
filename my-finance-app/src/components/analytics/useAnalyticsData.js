import { useState, useEffect } from 'react';
import { transactionsAPI } from '../../api';

const FALLBACK_COLORS = [
  '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6',
  '#EC4899', '#F97316', '#6366F1', '#14B8A6', '#06B6D4',
  '#64748B', '#475569', '#0EA5E9', '#A8A29E', '#4F46E5',
];

export function useAnalyticsData(transactionType, timePeriod, selectedDate) {
  const [loading, setLoading] = useState(true);
  const [categoryStats, setCategoryStats] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (!selectedDate) return;

    async function loadData() {
      setLoading(true);
      try {
        // Get date range for selected period
        const date = new Date(selectedDate);
        const { startDate, endDate } = getDateRange(date, timePeriod);

        // Load transactions for selected period only
        const res = await transactionsAPI.list({
          type: transactionType,
          start_date: startDate,
          end_date: endDate,
          limit: 1000
        });
        const transactions = res.data.results || [];
        const total = transactions.reduce((sum, tx) => sum + parseFloat(tx.amount), 0);

        // Group by category for selected period only
        const byCategory = {};
        transactions.forEach(tx => {
          const catName = tx.category_name || 'Без категории';
          const categoryColor = tx.category_color;

          if (!byCategory[catName]) {
            byCategory[catName] = {
              amount: 0,
              color: categoryColor
            };
          }
          byCategory[catName].amount += parseFloat(tx.amount);
        });

        // Assign fallback colors for categories without color
        let fallbackIndex = 0;
        const categories = Object.entries(byCategory).map(([category, data]) => {
          const color = data.color || FALLBACK_COLORS[fallbackIndex % FALLBACK_COLORS.length];
          fallbackIndex++;
          return {
            category,
            amount: data.amount,
            color,
            percentage: total > 0 ? ((data.amount / total) * 100).toFixed(1) : 0
          };
        }).sort((a, b) => b.amount - a.amount);

        setCategoryStats({ by_category: categories });
        setSummary({ total, count: transactions.length });

        // Prepare chart data
        const chartData = prepareChartData(transactions, timePeriod, date);
        setChartData(chartData);

      } catch (error) {
        console.error('Error loading analytics:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [transactionType, timePeriod, selectedDate]);

  return { loading, categoryStats, chartData, summary };
}

function getDateRange(date, timePeriod) {
  if (timePeriod === 'day') {
    const selectedDate = date.toISOString().split('T')[0];
    return {
      startDate: selectedDate + 'T00:00:00',
      endDate: selectedDate + 'T23:59:59'
    };
  }

  if (timePeriod === 'week') {
    const startOfWeek = new Date(date);
    startOfWeek.setDate(date.getDate() - startOfWeek.getDay());
    startOfWeek.setHours(0, 0, 0, 0);

    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);
    endOfWeek.setHours(23, 59, 59, 999);

    return {
      startDate: startOfWeek.toISOString(),
      endDate: endOfWeek.toISOString()
    };
  }

  // Month
  const startOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
  const endOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59);

  return {
    startDate: startOfMonth.toISOString(),
    endDate: endOfMonth.toISOString()
  };
}

function prepareChartData(transactions, timePeriod, date) {
  if (timePeriod === 'day') {
    const hourlyData = Array(24).fill(0);
    transactions.forEach(tx => {
      const txDate = new Date(tx.date);
      let mskHour = txDate.getUTCHours() + 3;
      if (mskHour >= 24) mskHour -= 24;
      hourlyData[mskHour] += parseFloat(tx.amount);
    });

    return {
      labels: Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`),
      data: hourlyData,
      title: 'По часам (МСК)'
    };
  }

  if (timePeriod === 'week') {
    const dayNames = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    const dailyData = Array(7).fill(0);
    transactions.forEach(tx => {
      const txDate = new Date(tx.date);
      dailyData[txDate.getUTCDay()] += parseFloat(tx.amount);
    });

    return {
      labels: dayNames,
      data: dailyData,
      title: 'По дням недели'
    };
  }

  // Month
  const daysInMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const dailyData = Array(daysInMonth).fill(0);
  transactions.forEach(tx => {
    const txDate = new Date(tx.date);
    const dayIndex = txDate.getUTCDate() - 1;
    if (dayIndex >= 0 && dayIndex < daysInMonth) {
      dailyData[dayIndex] += parseFloat(tx.amount);
    }
  });

  return {
    labels: Array.from({ length: daysInMonth }, (_, i) => String(i + 1)),
    data: dailyData,
    title: 'По дням месяца'
  };
}
