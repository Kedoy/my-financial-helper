import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { authAPI, blogAPI } from '../api';

export default function Profile() {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [fetchingProfile, setFetchingProfile] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    bio: '',
  });
  const [avatar, setAvatar] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Загружаем актуальный профиль при монтировании
  useEffect(() => {
    async function loadProfile() {
      if (!user) return;
      
      setFetchingProfile(true);
      try {
        // Пробуем загрузить с /auth/me/
        const response = await authAPI.getProfile();
        const profileData = response.data;
        
        setFormData({
          first_name: profileData.first_name || '',
          last_name: profileData.last_name || '',
          bio: profileData.profile?.bio || '',
        });
        
        if (profileData.profile?.avatar_url) {
          setAvatarPreview(profileData.profile.avatar_url);
        }
        
        // Обновляем user в localStorage с актуальными данными
        const updatedUser = { ...user, ...profileData };
        localStorage.setItem('user', JSON.stringify(updatedUser));
      } catch (error) {
        console.error('Error loading profile:', error);
      } finally {
        setFetchingProfile(false);
      }
    }
    
    loadProfile();
  }, [user]);

  function handleAvatarChange(e) {
    const file = e.target.files[0];
    if (file) {
      setAvatar(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      // Создаём FormData для отправки с изображением
      const data = new FormData();
      data.append('bio', formData.bio || '');

      if (avatar) {
        data.append('avatar', avatar);
      }

      const response = await blogAPI.profile.update(data);
      setMessage({ type: 'success', text: 'Профиль успешно обновлён!' });

      // Обновляем данные в localStorage из ответа сервера
      const serverData = response.data;
      const updatedUser = {
        ...user,
        first_name: formData.first_name,
        last_name: formData.last_name,
        profile: {
          ...user.profile,
          bio: serverData.bio || formData.bio,
          avatar_url: serverData.avatar_url || user.profile?.avatar_url
        }
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      // Уведомляем другие компоненты об обновлении аватарки
      window.dispatchEvent(new CustomEvent('avatar-updated', { detail: { avatarUrl: serverData.avatar_url } }));

      // Сброс аватара после загрузки
      if (avatar) {
        setAvatar(null);
        // Обновляем preview с URL от сервера
        if (serverData.avatar_url) {
          setAvatarPreview(serverData.avatar_url);
        }
      }
    } catch (error) {
      console.error('Profile update error:', error);
      setMessage({ type: 'error', text: 'Ошибка при обновлении профиля: ' + (error.response?.data?.message || error.message) });
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    logout();
    window.location.href = '/login';
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Мой профиль</h1>
        <p className="text-gray-600 mt-1">Управление личной информацией</p>
      </div>

      {/* Аватар */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex items-center space-x-6">
          <div className="relative">
            {avatarPreview ? (
              <img
                src={avatarPreview}
                alt="Аватар"
                className="w-24 h-24 rounded-full object-cover"
              />
            ) : (
              <div className="w-24 h-24 bg-gradient-to-br from-primary to-indigo-600 rounded-full flex items-center justify-center text-white text-4xl font-bold">
                {user?.first_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
              </div>
            )}
            <label className="absolute bottom-0 right-0 w-8 h-8 bg-primary hover:bg-indigo-700 rounded-full flex items-center justify-center text-white cursor-pointer transition shadow-lg">
              <i className="fas fa-camera text-sm"></i>
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="hidden"
              />
            </label>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {user?.first_name && user?.last_name
                ? `${user.first_name} ${user.last_name}`
                : user?.email}
            </h2>
            <p className="text-gray-600">{user?.email}</p>
            <button
              onClick={handleLogout}
              className="mt-2 text-danger hover:text-red-700 font-medium text-sm"
            >
              <i className="fas fa-sign-out-alt mr-2"></i>
              Выйти из аккаунта
            </button>
          </div>
        </div>
      </div>

      {/* Форма редактирования */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Редактирование профиля</h2>

        {message.text && (
          <div
            className={`mb-6 p-4 rounded-xl ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Имя
              </label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition"
                placeholder="Иван"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Фамилия
              </label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition"
                placeholder="Иванов"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              О себе
            </label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition resize-none"
              placeholder="Расскажите немного о себе..."
            />
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-primary hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl transition disabled:opacity-50"
            >
              {loading ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Сохранение...
                </>
              ) : (
                <>
                  <i className="fas fa-save mr-2"></i>
                  Сохранить изменения
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Информация об аккаунте */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Информация об аккаунте</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-1">Дата регистрации</p>
            <p className="text-lg font-semibold text-gray-900">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString('ru-RU', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })
                : '—'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Последний вход</p>
            <p className="text-lg font-semibold text-gray-900">
              {user?.last_login
                ? new Date(user.last_login).toLocaleDateString('ru-RU', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : '—'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
