import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    
    if (result.ok) {
      navigate('/');
    } else {
      setError(result.message);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-white to-secondary/10 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Карточка входа */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Заголовок */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-xl mb-4">
              <span className="text-white font-bold text-3xl">F</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Вход</h1>
            <p className="text-gray-600 mt-2">Введите данные для входа в аккаунт</p>
          </div>

          {/* Форма */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Пароль
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-xl">
                <i className="fas fa-exclamation-circle mr-2"></i>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl transition duration-200 disabled:opacity-50"
            >
              {loading ? 'Вход...' : 'Войти'}
            </button>
          </form>

          {/* Ссылка на регистрацию */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-primary hover:text-indigo-700 font-medium">
                Зарегистрироваться
              </Link>
            </p>
          </div>

          {/* Тестовые данные */}
          <div className="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <p className="text-sm text-gray-600 font-medium mb-2">
              <i className="fas fa-info-circle mr-2"></i>Тестовый вход:
            </p>
            <p className="text-xs text-gray-500">Email: admin@admin.com</p>
            <p className="text-xs text-gray-500">Пароль: admin123</p>
          </div>
        </div>
      </div>
    </div>
  );
}
