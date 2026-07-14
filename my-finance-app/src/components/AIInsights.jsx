import { useState, useEffect } from 'react';
import { analyticsAPI } from '../api';

export default function AIInsights({ days = 30 }) {
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInsights();
  }, [days]);

  async function loadInsights(forceRefresh = false) {
    setLoading(true);
    setError(null);
    try {
      const response = await analyticsAPI.aiInsights(days);
      setInsights(response.data.insights || []);
      setSummary(response.data.summary);
      
      if (response.data.insights?.length > 0 && response.data.insights[0]?.category === 'Ошибка подключения') {
        setError(response.data.insights[0].insight);
      } else if (forceRefresh && response.data.insights?.length === 0) {
        setError('AI не смог проанализировать данные. Попробуйте позже.');
      }
    } catch (err) {
      console.error('Error loading AI insights:', err);
      setError(err.response?.data?.message || 'Ошибка подключения к серверу');
    } finally {
      setLoading(false);
    }
  }

  function getInsightIcon(type) {
    switch (type) {
      case 'warning':
        return 'fa-triangle-exclamation text-amber-500';
      case 'success':
        return 'fa-circle-check text-green-500';
      case 'info':
      default:
        return 'fa-circle-info text-blue-500';
    }
  }

  function getInsightBg(type) {
    switch (type) {
      case 'warning':
        return 'bg-amber-50 border-amber-200';
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200';
    }
  }

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl shadow-sm p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
            <i className="fas fa-robot text-white text-lg"></i>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">AI Рекомендации</h2>
            <p className="text-sm text-gray-600">Персональные советы</p>
          </div>
        </div>
        <button
          onClick={() => loadInsights(true)}
          className="p-2 hover:bg-white/50 rounded-lg transition"
          title="Обновить (очистить кэш)"
        >
          <i className="fas fa-sync-alt text-gray-600"></i>
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white/70 backdrop-blur rounded-xl p-4">
            <p className="text-xs text-gray-600 mb-1">Доходы</p>
            <p className="text-lg font-bold text-green-600">
              {summary.total_income?.toLocaleString('ru-RU')} ₽
            </p>
          </div>
          <div className="bg-white/70 backdrop-blur rounded-xl p-4">
            <p className="text-xs text-gray-600 mb-1">Расходы</p>
            <p className="text-lg font-bold text-red-600">
              {summary.total_expenses?.toLocaleString('ru-RU')} ₽
            </p>
          </div>
          <div className="bg-white/70 backdrop-blur rounded-xl p-4">
            <p className="text-xs text-gray-600 mb-1">Баланс</p>
            <p className={`text-lg font-bold ${
              summary.balance >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {summary.balance?.toLocaleString('ru-RU')} ₽
            </p>
          </div>
        </div>
      )}

      {/* Insights */}
      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <i className="fas fa-exclamation-circle text-red-500 text-4xl mb-3"></i>
          <p className="text-red-700 font-semibold mb-2">AI-сервис временно недоступен</p>
          <p className="text-red-600 text-sm mb-4">{error}</p>
          <button
            onClick={loadInsights}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
          >
            <i className="fas fa-redo mr-2"></i>Попробовать снова
          </button>
        </div>
      ) : insights.length === 0 ? (
        <div className="text-center py-8">
          <i className="fas fa-robot text-gray-300 text-5xl mb-4"></i>
          <p className="text-gray-600">
            Добавьте транзакции для получения AI-рекомендаций
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`p-4 rounded-xl border ${getInsightBg(insight.type)} transition hover:shadow-md`}
            >
              <div className="flex items-start space-x-3">
                <i className={`fas ${getInsightIcon(insight.type)} text-lg mt-0.5`}></i>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-800 mb-1">
                    {insight.category}
                  </p>
                  <p className="text-sm text-gray-700">
                    {insight.insight}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-purple-200">
        <p className="text-xs text-gray-500 text-center">
          <i className="fas fa-cloud mr-1"></i>
          AI-рекомендации от внешнего сервиса
        </p>
      </div>
    </div>
  );
}
