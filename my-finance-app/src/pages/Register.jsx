import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password_confirm) {
      setError('Пароли не совпадают');
      return;
    }

    setLoading(true);
    const result = await register(formData);
    
    if (result.ok) {
      navigate('/');
    } else {
      setError(result.message);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-white to-secondary/10 flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary rounded-xl mb-4">
              <span className="text-white font-bold text-3xl">F</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Регистрация</h1>
            <p className="text-gray-600 mt-2">Создайте аккаунт для учёта финансов</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Имя пользователя</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition"
                placeholder="username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Пароль</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Подтверждение пароля</label>
              <input
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition"
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
              className="w-full bg-secondary hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-xl transition duration-200 disabled:opacity-50"
            >
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-secondary hover:text-green-700 font-medium">
                Войти
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
