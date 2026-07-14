import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { transactionsAPI, analyticsAPI } from '../api';
import AddTransactionModal from '../components/AddTransactionModal';

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [groupedByDay, setGroupedByDay] = useState({});
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsRes, transactionsRes] = await Promise.all([
        analyticsAPI.summary(30),
        transactionsAPI.list({ limit: 100 }),
      ]);

      setStats(statsRes.data);
      setTransactions(transactionsRes.data.results || []);

      // Группируем по дням
      const grouped = groupTransactionsByDay(transactionsRes.data.results || []);
      setGroupedByDay(grouped);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }

  function handleTransactionSuccess() {
    loadData();
  }

  function groupTransactionsByDay(transactions) {
    const groups = {};
    
    transactions.forEach(tx => {
      const date = new Date(tx.date).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
      
      if (!groups[date]) {
        groups[date] = {
          date: new Date(tx.date).toISOString().split('T')[0],
          fullDate: date,
          expenses: 0,
          income: 0,
          transactions: []
        };
      }
      
      groups[date].transactions.push(tx);
      if (tx.type === 'expense') {
        groups[date].expenses += parseFloat(tx.amount);
      } else {
        groups[date].income += parseFloat(tx.amount);
      }
    });
    
    return groups;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Заголовок */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Главная</h1>
          <p className="text-gray-600 mt-1">Обзор ваших финансов</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-primary hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-medium transition flex items-center"
        >
          <i className="fas fa-plus mr-2"></i>
          Добавить
        </button>
      </div>

      {/* Карточки статистики */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Баланс */}
        <div className="bg-white rounded-2xl shadow-sm p-6 border-l-4 border-primary">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Общий баланс</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.balance?.toFixed(2) || '0'} ₽
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <i className="fas fa-wallet text-primary text-xl"></i>
            </div>
          </div>
        </div>

        {/* Расходы */}
        <div className="bg-white rounded-2xl shadow-sm p-6 border-l-4 border-danger">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Расходы за месяц</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.total_expenses?.toFixed(2) || '0'} ₽
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <i className="fas fa-arrow-down text-danger text-xl"></i>
            </div>
          </div>
        </div>

        {/* Доходы */}
        <div className="bg-white rounded-2xl shadow-sm p-6 border-l-4 border-secondary">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Доходы за месяц</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.total_income?.toFixed(2) || '0'} ₽
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <i className="fas fa-arrow-up text-secondary text-xl"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Карточки дней */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">История операций</h2>
        
        {Object.keys(groupedByDay).length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
            <i className="fas fa-receipt text-gray-300 text-6xl mb-4"></i>
            <p className="text-gray-600">Пока нет транзакций</p>
            <Link to="/transactions" className="text-primary hover:text-indigo-700 font-medium mt-2 inline-block">
              Добавить первую транзакцию
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(groupedByDay).map(([day, data]) => (
              <DayCard key={day} day={day} data={data} />
            ))}
          </div>
        )}
      </div>

      {/* Modal for adding transaction */}
      <AddTransactionModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={handleTransactionSuccess}
      />
    </div>
  );
}

function DayCard({ day, data }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
      {/* Заголовок дня */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="text-center w-16">
              <div className="text-2xl font-bold text-gray-900">
                {new Date(data.date).getDate()}
              </div>
              <div className="text-xs text-gray-500 uppercase">
                {new Date(data.date).toLocaleDateString('ru-RU', { month: 'short' })}
              </div>
            </div>
            <div>
              <p className="font-medium text-gray-900">{day}</p>
              <p className="text-sm text-gray-500">
                {data.transactions.length} транзакций
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="text-right">
              <p className="text-sm text-danger">
                -{data.expenses.toFixed(2)} ₽
              </p>
              <p className="text-sm text-secondary">
                +{data.income.toFixed(2)} ₽
              </p>
            </div>
            <i
              className={`fas fa-chevron-down text-gray-400 transition-transform ${
                expanded ? 'rotate-180' : ''
              }`}
            ></i>
          </div>
        </div>
      </div>

      {/* Список транзакций */}
      {expanded && (
        <div className="border-t border-gray-200 divide-y divide-gray-100">
          {data.transactions.map((tx) => (
            <div key={tx.id} className="p-4 hover:bg-gray-50 transition">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      tx.type === 'expense'
                        ? 'bg-red-100'
                        : 'bg-green-100'
                    }`}
                  >
                    <i
                      className={`fas ${
                        tx.type === 'expense'
                          ? 'fa-arrow-down text-danger'
                          : 'fa-arrow-up text-secondary'
                      }`}
                    ></i>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {tx.description || 'Без описания'}
                    </p>
                    <p className="text-sm text-gray-500">
                      {tx.category_name || 'Без категории'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p
                    className={`font-bold ${
                      tx.type === 'expense'
                        ? 'text-danger'
                        : 'text-secondary'
                    }`}
                  >
                    {tx.type === 'expense' ? '-' : '+'}
                    {parseFloat(tx.amount).toFixed(2)} ₽
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(tx.date).toLocaleTimeString('ru-RU', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
