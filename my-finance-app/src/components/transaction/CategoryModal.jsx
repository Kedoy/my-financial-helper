import { useState } from 'react';

const PRESET_COLORS = [
  '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6',
  '#EC4899', '#F97316', '#6366F1', '#14B8A6', '#06B6D4',
  '#64748B', '#475569', '#0EA5E9', '#A8A29E', '#4F46E5',
];

export default function CategoryModal({ isOpen, onClose, onSubmit, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    type: 'expense',
    icon: 'shopping_cart',
    color: '#4F46E5',
  });
  const [showColorPicker, setShowColorPicker] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit(formData);
  }

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 m-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Новая категория</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <i className="fas fa-times text-xl"></i>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Название
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Например: Продукты"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Тип
            </label>
            <div className="flex space-x-4">
              <label className="flex-1">
                <input
                  type="radio"
                  name="categoryType"
                  value="expense"
                  checked={formData.type === 'expense'}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex items-center justify-center py-2 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-danger peer-checked:bg-red-50 peer-checked:text-danger transition">
                  <i className="fas fa-arrow-down mr-2"></i>
                  <span>Расход</span>
                </div>
              </label>
              <label className="flex-1">
                <input
                  type="radio"
                  name="categoryType"
                  value="income"
                  checked={formData.type === 'income'}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex items-center justify-center py-2 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-secondary peer-checked:bg-green-50 peer-checked:text-secondary transition">
                  <i className="fas fa-arrow-up mr-2"></i>
                  <span>Доход</span>
                </div>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Иконка
            </label>
            <div className="relative">
              <select
                value={formData.icon}
                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent appearance-none"
              >
                <option value="shopping_cart">🛒 Продукты</option>
                <option value="car">🚗 Транспорт</option>
                <option value="home">🏠 Дом</option>
                <option value="utilities">💡 Коммуналка</option>
                <option value="entertainment">🎬 Развлечения</option>
                <option value="health">🏥 Здоровье</option>
                <option value="education">📚 Образование</option>
                <option value="salary">💰 Зарплата</option>
                <option value="investment">📈 Инвестиции</option>
                <option value="gift">🎁 Подарки</option>
              </select>
              <i className="fas fa-chevron-down absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none"></i>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Цвет
            </label>
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={() => setShowColorPicker(!showColorPicker)}
                className="w-12 h-12 rounded-xl border-2 border-gray-300 hover:border-gray-400 transition"
                style={{ backgroundColor: formData.color }}
              />
              <input
                type="text"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="#4F46E5"
              />
            </div>

            {showColorPicker && (
              <div className="grid grid-cols-5 gap-2 p-3 bg-gray-50 rounded-xl border border-gray-200 mt-2">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => {
                      setFormData({ ...formData, color });
                      setShowColorPicker(false);
                    }}
                    className="w-full aspect-square rounded-lg hover:scale-110 transition transform border-2 border-transparent hover:border-gray-400"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            )}
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
                  <span>Создать</span>
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
