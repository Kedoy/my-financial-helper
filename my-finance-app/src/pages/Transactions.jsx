import { useState, useEffect } from 'react';
import { transactionsAPI, categoriesAPI } from '../api';

export default function Transactions() {
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [deletePendingId, setDeletePendingId] = useState(null);
  const [filters, setFilters] = useState({
    type: '',
    category: '',
    date: '',
  });
  const [showCalendar, setShowCalendar] = useState(false);
  const [availableDates, setAvailableDates] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [txRes, catRes] = await Promise.all([
        transactionsAPI.list(),
        categoriesAPI.list(),
      ]);

      setTransactions(txRes.data.results || []);
      setCategories(catRes.data.results || []);
      
      // Получаем доступные даты
      const dates = txRes.data.results.map(tx => 
        new Date(tx.date).toISOString().split('T')[0]
      );
      setAvailableDates([...new Set(dates)]);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }

  async function applyFilters() {
    setLoading(true);
    try {
      const params = {};
      if (filters.type) params.type = filters.type;
      if (filters.category) params.category = filters.category;
      if (filters.date) {
        params.start_date = filters.date + 'T00:00:00';
        params.end_date = filters.date + 'T23:59:59';
      }

      const response = await transactionsAPI.list(params);
      setTransactions(response.data.results || []);
      setShowCalendar(false);
    } catch (error) {
      console.error('Error filtering:', error);
    } finally {
      setLoading(false);
    }
  }

  function resetFilters() {
    setFilters({
      type: '',
      category: '',
      date: '',
    });
    loadData();
  }

  function handleDeleteClick(id) {
    if (deletePendingId === id) {
      // Second click - confirm deletion
      deleteTransaction(id);
      setDeletePendingId(null);
    } else {
      // First click - show confirmation
      setDeletePendingId(id);
      // Auto-cancel after 3 seconds
      setTimeout(() => {
        setDeletePendingId(null);
      }, 3000);
    }
  }

  async function deleteTransaction(id) {
    try {
      await transactionsAPI.delete(id);
      loadData();
    } catch (error) {
      console.error('Error deleting transaction:', error);
      const errorMsg = error.response?.data?.error || error.message;
      alert('Ошибка: ' + errorMsg);
    }
  }

  function isDateAvailable(date) {
    return availableDates.includes(date);
  }

  function isDateDisabled(date) {
    const today = new Date().toISOString().split('T')[0];
    return date > today;
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">История операций</h1>
        <p className="text-gray-600 mt-1">Все ваши транзакции</p>
      </div>

      {/* Фильтры */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">Все типы</option>
            <option value="expense">Расходы</option>
            <option value="income">Доходы</option>
          </select>

          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">Все категории</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>

          <div className="relative">
            <button
              onClick={() => setShowCalendar(!showCalendar)}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent text-left bg-white hover:bg-gray-50 transition"
            >
              {filters.date ? (
                <span>{new Date(filters.date).toLocaleDateString('ru-RU')}</span>
              ) : (
                <span className="text-gray-500">Выберите дату</span>
              )}
            </button>

            {showCalendar && (
              <div className="absolute z-10 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 p-4 w-80">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-gray-900">Календарь</h3>
                  <button
                    onClick={() => setShowCalendar(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
                <Calendar
                  value={filters.date}
                  onChange={(date) => {
                    setFilters({ ...filters, date });
                    setShowCalendar(false);
                  }}
                  availableDates={availableDates}
                  isDateDisabled={isDateDisabled}
                />
                <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-100 rounded"></div>
                    <span>Есть транзакции</span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="w-3 h-3 bg-gray-100 rounded"></div>
                    <span>Нет данных</span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="w-3 h-3 bg-gray-50 rounded line-through"></div>
                    <span>Недоступно</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex space-x-2">
            <button
              onClick={applyFilters}
              className="flex-1 bg-primary hover:bg-indigo-700 text-white px-4 py-2 rounded-xl transition"
            >
              <i className="fas fa-filter mr-2"></i>
              Фильтр
            </button>
            <button
              onClick={resetFilters}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-xl transition"
            >
              <i className="fas fa-redo"></i>
            </button>
          </div>
        </div>
      </div>

      {/* Список транзакций */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : transactions.length === 0 ? (
          <div className="p-12 text-center">
            <i className="fas fa-receipt text-gray-300 text-6xl mb-4"></i>
            <p className="text-gray-600">Нет транзакций</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Описание</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Категория</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Сумма</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map((tx) => {
                  const isPending = deletePendingId === tx.id;
                  return (
                    <tr key={tx.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(tx.date).toLocaleDateString('ru-RU')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {tx.description || '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {tx.category_name || (
                          <span className="text-gray-400">Без категории</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`font-bold ${
                            tx.type === 'expense' ? 'text-danger' : 'text-secondary'
                          }`}
                        >
                          {tx.type === 'expense' ? '-' : '+'}
                          {parseFloat(tx.amount).toFixed(2)} ₽
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end space-x-1">
                          {isPending ? (
                            <button
                              onClick={() => deleteTransaction(tx.id)}
                              className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg transition animate-pulse text-xs font-medium"
                              title="Подтвердить удаление"
                            >
                              <i className="fas fa-check mr-1"></i>
                              OK
                            </button>
                          ) : (
                            <button
                              onClick={() => handleDeleteClick(tx.id)}
                              className="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded-lg transition"
                              title="Удалить"
                            >
                              <i className="fas fa-trash"></i>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function Calendar({ value, onChange, availableDates, isDateDisabled }) {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const daysInMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth() + 1,
    0
  ).getDate();

  const firstDayOfMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth(),
    1
  ).getDay();

  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];

  function formatDate(year, month, day) {
    const m = (month + 1).toString().padStart(2, '0');
    const d = day.toString().padStart(2, '0');
    return `${year}-${m}-${d}`;
  }

  function goToPreviousMonth() {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  }

  function goToNextMonth() {
    const today = new Date();
    if (currentMonth.getMonth() < today.getMonth() || 
        currentMonth.getFullYear() < today.getFullYear()) {
      setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
    }
  }

  return (
    <div>
      {/* Заголовок календаря */}
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={goToPreviousMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <i className="fas fa-chevron-left"></i>
        </button>
        <span className="font-bold text-gray-900">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </span>
        <button
          onClick={goToNextMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
          disabled={
            currentMonth.getMonth() >= new Date().getMonth() &&
            currentMonth.getFullYear() >= new Date().getFullYear()
          }
        >
          <i className="fas fa-chevron-right"></i>
        </button>
      </div>

      {/* Дни недели */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map((day) => (
          <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Дни месяца */}
      <div className="grid grid-cols-7 gap-1">
        {/* Пустые ячейки до первого дня месяца */}
        {Array(firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1)
          .fill(null)
          .map((_, i) => (
            <div key={`empty-${i}`} className="aspect-square"></div>
          ))}

        {/* Дни месяца */}
        {Array(daysInMonth)
          .fill(null)
          .map((_, i) => {
            const day = i + 1;
            const dateStr = formatDate(currentMonth.getFullYear(), currentMonth.getMonth(), day);
            const isAvailable = availableDates.includes(dateStr);
            const disabled = isDateDisabled(dateStr);
            const isSelected = value === dateStr;

            return (
              <button
                key={day}
                onClick={() => !disabled && onChange(dateStr)}
                disabled={disabled}
                className={`
                  aspect-square rounded-lg text-sm font-medium transition
                  ${isSelected ? 'bg-primary text-white' : ''}
                  ${!isSelected && isAvailable && !disabled ? 'bg-green-100 text-gray-900 hover:bg-green-200' : ''}
                  ${!isAvailable && !disabled ? 'bg-gray-100 text-gray-400 hover:bg-gray-200' : ''}
                  ${disabled ? 'bg-gray-50 text-gray-300 cursor-not-allowed line-through' : ''}
                `}
              >
                {day}
              </button>
            );
          })}
      </div>
    </div>
  );
}
