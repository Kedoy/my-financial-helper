import { useState, useEffect } from 'react';

export default function PostModal({ isOpen, onClose, onSubmit, editingPost }) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    visibility: 'public',
  });
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingPost) {
      setFormData({
        title: editingPost.title || '',
        content: editingPost.content || '',
        visibility: editingPost.visibility || 'public',
      });
      setImage(null);
      setImagePreview(editingPost.image_url);
    } else {
      resetForm();
    }
  }, [editingPost, isOpen]);

  function resetForm() {
    setFormData({
      title: '',
      content: '',
      visibility: 'public',
    });
    setImage(null);
    setImagePreview(null);
  }

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      await onSubmit({ ...formData, image });
      resetForm();
      onClose();
    } catch (error) {
      console.error('Error creating post:', error);
      alert('Ошибка при создании поста: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6 p-6 border-b border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900">
            {editingPost ? 'Редактировать пост' : 'Новый пост'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <i className="fas fa-times text-xl"></i>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Заголовок
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              maxLength={200}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="О чём ваша заметка?"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Содержимое
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              required
              rows={6}
              maxLength={5000}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              placeholder="Поделитесь своими мыслями о финансовой грамотности..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Изображение (необязательно)
            </label>
            <div className="flex items-center space-x-4">
              <label className="flex-1">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="hidden"
                />
                <div className="flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-primary transition">
                  <i className="fas fa-image text-gray-400 mr-2"></i>
                  <span className="text-sm text-gray-600">
                    {image ? image.name : 'Выберите изображение'}
                  </span>
                </div>
              </label>
              {imagePreview && (
                <button
                  type="button"
                  onClick={() => {
                    setImage(null);
                    setImagePreview(null);
                  }}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition"
                  title="Удалить изображение"
                >
                  <i className="fas fa-trash"></i>
                </button>
              )}
            </div>
            {imagePreview && (
              <div className="mt-3">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full h-48 object-cover rounded-xl"
                />
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Видимость
            </label>
            <div className="flex space-x-4">
              <label className="flex-1">
                <input
                  type="radio"
                  name="visibility"
                  value="public"
                  checked={formData.visibility === 'public'}
                  onChange={(e) => setFormData({ ...formData, visibility: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex items-center justify-center py-3 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-primary peer-checked:bg-indigo-50 peer-checked:text-primary transition">
                  <i className="fas fa-globe mr-2"></i>
                  <span>Публичный</span>
                </div>
              </label>
              <label className="flex-1">
                <input
                  type="radio"
                  name="visibility"
                  value="private"
                  checked={formData.visibility === 'private'}
                  onChange={(e) => setFormData({ ...formData, visibility: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex items-center justify-center py-3 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-primary peer-checked:bg-indigo-50 peer-checked:text-primary transition">
                  <i className="fas fa-lock mr-2"></i>
                  <span>Приватный</span>
                </div>
              </label>
            </div>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center bg-primary hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  <span>Сохранение...</span>
                </>
              ) : (
                <>
                  <i className="fas fa-save mr-2"></i>
                  <span>{editingPost ? 'Сохранить' : 'Опубликовать'}</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 flex items-center justify-center bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-4 rounded-xl transition"
            >
              <span>Отмена</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
