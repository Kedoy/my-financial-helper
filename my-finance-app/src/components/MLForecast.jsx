import { useState, useEffect } from 'react';
import { analyticsAPI } from '../api';

export default function MLForecast({ selectedCategory = null, categoryName = '' }) {
  const [loading, setLoading] = useState(false);
  const [forecast, setForecast] = useState(null);
  const [dailyForecasts, setDailyForecasts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState(null);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [selectedDate, setSelectedDate] = useState('');

  useEffect(() => {
    loadForecast();
  }, [selectedCategory, selectedPeriod]);

  async function loadForecast(forceRefresh = false) {
    setLoading(true);
    setError(null);
    try {
      const response = await analyticsAPI.forecast('daily', selectedPeriod, selectedCategory, !forceRefresh);
      
      if (response.data.success) {
        setForecast(response.data);
        setSummary(response.data.summary);
        setTrend(response.data.trend);
        setDailyForecasts(response.data.daily_forecasts || []);
        
        if (response.data.daily_forecasts && response.data.daily_forecasts.length > 0) {
          setSelectedDate(response.data.daily_forecasts[0].date);
        }
      } else {
        setError(response.data.error || 'Прогноз недоступен');
      }
    } catch (err) {
      console.error('Error loading ML forecast:', err);
      setError(err.response?.data?.error || 'Ошибка подключения к серверу');
    } finally {
      setLoading(false);
    }
  }

  function getForecastForSelectedDate() {
    if (!selectedDate || !dailyForecasts.length) return null;
    return dailyForecasts.find(f => f.date === selectedDate);
  }

  const selectedDayForecast = getForecastForSelectedDate();

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl shadow-sm p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
            <i className="fas fa-chart-line text-white text-lg"></i>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Прогноз расходов {categoryName ? `: ${categoryName}` : ''}
            </h2>
            <p className="text-sm text-gray-600">AI предскажет сколько вы потратите</p>
          </div>
        </div>
        <button
          onClick={() => loadForecast(true)}
          className="p-2 hover:bg-white/50 rounded-lg transition"
          title="Обновить прогноз"
        >
          <i className="fas fa-sync-alt text-gray-600"></i>
        </button>
      </div>

      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <i className="fas fa-exclamation-circle text-red-500 text-4xl mb-3"></i>
          <p className="text-red-700 font-semibold mb-2">Прогноз недоступен</p>
          <p className="text-red-600 text-sm mb-4">{error}</p>
          <button
            onClick={loadForecast}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
          >
            <i className="fas fa-redo mr-2"></i>Попробовать снова
          </button>
        </div>
      ) : !summary ? (
        <div className="text-center py-8">
          <i className="fas fa-chart-line text-gray-300 text-5xl mb-4"></i>
          <p className="text-gray-600">Недостаточно данных для прогноза</p>
          <p className="text-gray-500 text-sm mt-2">Добавьте минимум 30 транзакций</p>
        </div>
      ) : (
        <>
          {/* 1. Выбор периода */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-700 uppercase">
                <i className="fas fa-calendar-alt mr-2"></i>
                На какой период сделать прогноз?
              </span>
            </div>
            <div className="flex gap-2">
              {[7, 14, 30, 60].map(period => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`flex-1 py-3 text-sm font-bold rounded-xl transition-all ${
                    selectedPeriod === period
                      ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg scale-105'
                      : 'bg-white text-gray-700 hover:bg-white hover:scale-105'
                  }`}
                >
                  {period} дн
                </button>
              ))}
            </div>
          </div>

          {/* 2. Главный прогноз - сколько потратим */}
          <div className="bg-white rounded-2xl p-6 mb-6 shadow-sm border-2 border-emerald-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-gray-700 uppercase">
                <i className="fas fa-wallet text-emerald-600 mr-2"></i>
                Прогноз расходов
              </h3>
              <span className="text-xs text-gray-500">на {selectedPeriod} дней</span>
            </div>
            
            <div className="text-center py-4">
              <p className="text-5xl font-bold text-emerald-600 mb-2">
                {summary.total_predicted?.toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽
              </p>
              <p className="text-gray-600">
                ≈ {summary.average_daily?.toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽ в день
              </p>
            </div>

            {/* Диапазон */}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  <i className="fas fa-shield-alt text-green-500 mr-1"></i>
                  Минимум:
                </span>
                <span className="font-bold text-green-600">
                  {summary.lower_bound?.toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽
                </span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-gray-600">
                  <i className="fas fa-arrow-up text-red-500 mr-1"></i>
                  Максимум:
                </span>
                <span className="font-bold text-red-600">
                  {summary.upper_bound?.toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-3 text-center">
                С точностью {summary.confidence_level?.toFixed(0)}% вы потратите от 
                {summary.lower_bound?.toLocaleString()} до {summary.upper_bound?.toLocaleString()} ₽
              </p>
            </div>
          </div>

          {/* 3. Выбор конкретной даты */}
          {dailyForecasts.length > 0 && (
            <div className="bg-white rounded-xl p-5 mb-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-700">
                  <i className="fas fa-calendar-day text-blue-600 mr-2"></i>
                  Прогноз на конкретный день
                </h3>
                <span className="text-xs text-gray-500">
                  {dailyForecasts.length} дней доступно
                </span>
              </div>

              {/* Select с датами */}
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full p-3 border-2 border-gray-200 rounded-xl text-gray-700 font-medium focus:border-emerald-500 focus:outline-none transition mb-4"
              >
                {dailyForecasts.map((forecast, index) => {
                  const date = new Date(forecast.date);
                  const dayName = date.toLocaleDateString('ru-RU', { weekday: 'long' });
                  const dayDate = date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
                  return (
                    <option key={forecast.date} value={forecast.date}>
                      {dayName}, {dayDate} (день {index + 1})
                    </option>
                  );
                })}
              </select>

              {/* Детали выбранного дня */}
              {selectedDayForecast && (
                <div className="bg-gradient-to-r from-blue-50 to-emerald-50 rounded-xl p-5 border-2 border-blue-200">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Прогноз на день:</p>
                      <p className="text-3xl font-bold text-blue-600">
                        {selectedDayForecast.predicted?.toLocaleString('ru-RU', { 
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 0 
                        })} ₽
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-600 mb-1">Диапазон:</p>
                      <p className="text-sm font-bold text-gray-700">
                        {selectedDayForecast.lower_bound?.toLocaleString()} - 
                        {selectedDayForecast.upper_bound?.toLocaleString()} ₽
                      </p>
                    </div>
                  </div>
                  
                  {/* Визуализация диапазона */}
                  <div className="mt-4">
                    <div className="relative h-3 bg-gradient-to-r from-green-200 via-blue-300 to-red-200 rounded-full">
                      <div 
                        className="absolute top-1/2 transform -translate-y-1/2 w-4 h-4 bg-blue-600 border-2 border-white rounded-full shadow-lg"
                        style={{ 
                          left: `${((selectedDayForecast.predicted - selectedDayForecast.lower_bound) / 
                                   (selectedDayForecast.upper_bound - selectedDayForecast.lower_bound)) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <div className="flex justify-between mt-2 text-xs text-gray-500">
                      <span>Мин: {selectedDayForecast.lower_bound?.toLocaleString()} ₽</span>
                      <span>Макс: {selectedDayForecast.upper_bound?.toLocaleString()} ₽</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 6. Статистика периода */}
          {dailyForecasts.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-700">
                  <i className="fas fa-chart-bar text-blue-600 mr-2"></i>
                  Статистика на период
                </h3>
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-4 bg-green-50 rounded-xl">
                  <p className="text-xs text-gray-600 mb-2">Минимум в день</p>
                  <p className="text-xl font-bold text-green-600">
                    {Math.min(...dailyForecasts.map(f => f.predicted)).toLocaleString()} ₽
                  </p>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-xl">
                  <p className="text-xs text-gray-600 mb-2">Максимум в день</p>
                  <p className="text-xl font-bold text-red-600">
                    {Math.max(...dailyForecasts.map(f => f.predicted)).toLocaleString()} ₽
                  </p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-xl">
                  <p className="text-xs text-gray-600 mb-2">Среднее</p>
                  <p className="text-xl font-bold text-blue-600">
                    {summary.average_daily?.toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
