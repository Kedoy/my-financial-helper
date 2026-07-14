import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useState, useEffect } from 'react';
import { authAPI } from '../api';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [avatarUrl, setAvatarUrl] = useState(null);

  // Загружаем актуальную аватарку при монтировании
  useEffect(() => {
    async function loadAvatar() {
      if (!user) return;
      
      try {
        const response = await authAPI.getProfile();
        const profileData = response.data;
        
        if (profileData.profile?.avatar_url) {
          setAvatarUrl(profileData.profile.avatar_url);
        }
      } catch (error) {
        console.error('Error loading avatar:', error);
      }
    }
    
    loadAvatar();
    
    // Слушаем событие обновления аватарки
    function handleAvatarUpdate(event) {
      if (event.detail?.avatarUrl) {
        setAvatarUrl(event.detail.avatarUrl);
      }
    }
    
    window.addEventListener('avatar-updated', handleAvatarUpdate);
    
    return () => {
      window.removeEventListener('avatar-updated', handleAvatarUpdate);
    };
  }, [user]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  const getUserInitials = () => {
    if (user?.first_name || user?.last_name) {
      return `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`.toUpperCase();
    }
    return user?.email?.[0]?.toUpperCase() || 'U';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header сверху */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Логотип */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">₽</span>
                </div>
                <span className="text-lg font-bold text-gray-900">Финансовый Помощник</span>
              </Link>

              {/* Навигация */}
              <nav className="hidden md:flex ml-10 space-x-1">
                <Link
                  to="/"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <i className="fas fa-home mr-2"></i>Главная
                </Link>
                <Link
                  to="/analytics"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/analytics')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <i className="fas fa-chart-pie mr-2"></i>Аналитика
                </Link>
                <Link
                  to="/transactions"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/transactions')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <i className="fas fa-list mr-2"></i>История
                </Link>
                <Link
                  to="/categories"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/categories')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <i className="fas fa-tags mr-2"></i>Категории
                </Link>
                <Link
                  to="/blog"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/blog')
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <i className="fas fa-newspaper mr-2"></i>Блог
                </Link>
              </nav>
            </div>

            {/* Профиль */}
            <div className="flex items-center space-x-4">
              <Link
                to="/profile"
                className="flex items-center space-x-2 text-gray-700 hover:text-primary transition"
              >
                {avatarUrl ? (
                  <img
                    src={avatarUrl}
                    alt="Аватар"
                    className="w-8 h-8 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-8 h-8 bg-gradient-to-br from-primary to-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {getUserInitials()}
                  </div>
                )}
                <span className="text-sm font-medium hidden sm:block">{user?.email}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="text-gray-700 hover:text-danger transition p-2"
                title="Выйти"
              >
                <i className="fas fa-sign-out-alt"></i>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Основной контент */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
