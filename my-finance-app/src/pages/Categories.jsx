import { useState, useEffect } from 'react';
import { categoriesAPI, transactionsAPI } from '../api';

export default function Categories() {
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showTransactionsModal, setShowTransactionsModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categoryTransactions, setCategoryTransactions] = useState([]);
  const [deletePendingId, setDeletePendingId] = useState(null);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'expense',
    icon: 'shopping_cart',
    color: '#4F46E5',
  });

  // Закрываем color picker при закрытии модального окна
  useEffect(() => {
    if (!showModal) {
      setShowColorPicker(false);
    }
  }, [showModal]);

  useEffect(() => {
    loadCategories();
  }, []);

  async function loadCategories() {
    try {
      const response = await categoriesAPI.list();
      setCategories(response.data.results || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    } finally {
      setLoading(false);
    }
  }

  function openCreateModal() {
    setEditingCategory(null);
    setFormData({
      name: '',
      type: 'expense',
      icon: 'shopping_cart',
      color: '#4F46E5',
    });
    setShowModal(true);
  }

  function openEditModal(category) {
    if (category.is_system) {
      alert('Системные категории нельзя редактировать');
      return;
    }
    setEditingCategory(category);
    setFormData({
      name: category.name,
      type: category.type,
      icon: category.icon || 'shopping_cart',
      color: category.color || '#4F46E5',
    });
    setShowModal(true);
  }

  async function openTransactionsModal(category) {
    setSelectedCategory(category);
    try {
      const response = await transactionsAPI.list({ category: category.id });
      setCategoryTransactions(response.data.results || []);
      setShowTransactionsModal(true);
    } catch (error) {
      console.error('Error loading transactions:', error);
      alert('Ошибка при загрузке транзакций');
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (editingCategory?.is_system) {
      alert('Системные категории нельзя редактировать');
      setShowModal(false);
      return;
    }

    try {
      if (editingCategory) {
        await categoriesAPI.update(editingCategory.id, formData);
      } else {
        await categoriesAPI.create(formData);
      }

      setShowModal(false);
      loadCategories();
    } catch (error) {
      console.error('Error saving category:', error);
      const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message;
      alert('Ошибка при сохранении категории: ' + errorMsg);
    }
  }

  function handleColorChange(color) {
    setFormData({ ...formData, color });
    setShowColorPicker(false);
  }

  const presetColors = [
    '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6',
    '#EC4899', '#F97316', '#6366F1', '#14B8A6', '#06B6D4',
    '#64748B', '#475569', '#0EA5E9', '#A8A29E', '#4F46E5',
  ];

  function handleDeleteClick(id) {
    if (deletePendingId === id) {
      deleteCategory(id);
      setDeletePendingId(null);
    } else {
      setDeletePendingId(id);
      setTimeout(() => {
        setDeletePendingId(null);
      }, 3000);
    }
  }

  async function deleteCategory(id) {
    try {
      await categoriesAPI.delete(id);
      loadCategories();
    } catch (error) {
      console.error('Error deleting category:', error);
      const errorMsg = error.response?.data?.error || error.message;
      alert('Ошибка: ' + errorMsg);
    }
  }

  function calculateCategoryStats(transactions, type) {
    return transactions
      .filter(tx => tx.type === type)
      .reduce((sum, tx) => sum + parseFloat(tx.amount), 0);
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Категории</h1>
          <p className="text-gray-600 mt-1">Управление категориями расходов и доходов</p>
        </div>
        <button
          onClick={openCreateModal}
          className="bg-primary hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-medium transition flex items-center"
        >
          <i className="fas fa-plus mr-2"></i>
          Создать категорию
        </button>
      </div>

      {/* Список категорий */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : categories.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
          <i className="fas fa-tags text-gray-300 text-6xl mb-4"></i>
          <p className="text-gray-600">Нет категорий</p>
          <button
            onClick={openCreateModal}
            className="text-primary hover:text-indigo-700 font-medium mt-2 inline-block"
          >
            Создать первую категорию
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <CategoryCard
              key={category.id}
              category={category}
              onEdit={openEditModal}
              onViewTransactions={openTransactionsModal}
              deletePendingId={deletePendingId}
              onDeleteClick={handleDeleteClick}
            />
          ))}
        </div>
      )}

      {/* Модальное окно создания/редактирования */}
      {showModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setShowModal(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 m-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {editingCategory ? 'Редактировать категорию' : 'Новая категория'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
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
                      name="type"
                      value="expense"
                      checked={formData.type === 'expense'}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="peer sr-only"
                    />
                    <div className="text-center py-2 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-danger peer-checked:bg-red-50 peer-checked:text-danger transition">
                      <i className="fas fa-arrow-down mr-2"></i>Расход
                    </div>
                  </label>
                  <label className="flex-1">
                    <input
                      type="radio"
                      name="type"
                      value="income"
                      checked={formData.type === 'income'}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="peer sr-only"
                    />
                    <div className="text-center py-2 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-secondary peer-checked:bg-green-50 peer-checked:text-secondary transition">
                      <i className="fas fa-arrow-up mr-2"></i>Доход
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Цвет
                </label>
                <div className="space-y-2">
                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={() => setShowColorPicker(!showColorPicker)}
                      className="w-12 h-10 rounded-lg border-2 border-gray-300 cursor-pointer hover:border-primary transition"
                      style={{ backgroundColor: formData.color }}
                      title="Выбрать цвет"
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
                    <div className="grid grid-cols-5 gap-2 p-3 bg-gray-50 rounded-xl border border-gray-200">
                      {presetColors.map((color) => (
                        <button
                          key={color}
                          type="button"
                          onClick={() => handleColorChange(color)}
                          className="w-full aspect-square rounded-lg hover:scale-110 transition transform border-2 border-transparent hover:border-gray-400"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-primary hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl transition"
                >
                  <i className="fas fa-save mr-2"></i>
                  Сохранить
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-4 rounded-xl transition"
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальное окно просмотра транзакций категории */}
      {showTransactionsModal && selectedCategory && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setShowTransactionsModal(false)}
        >
          <div 
            className="bg-white rounded-2xl shadow-xl max-w-2xl w-full m-4 max-h-[90vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: `${selectedCategory.color}20` }}
                  >
                    <i
                      className={`fas fa-${selectedCategory.icon || 'tag'}`}
                      style={{ color: selectedCategory.color }}
                    ></i>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{selectedCategory.name}</h3>
                    <p className="text-sm text-gray-500">
                      {selectedCategory.type === 'expense' ? 'Расход' : 'Доход'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowTransactionsModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>

              {/* Stats */}
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="bg-red-50 rounded-xl p-3">
                  <p className="text-xs text-gray-600">Расходы</p>
                  <p className="text-lg font-bold text-danger">
                    -{calculateCategoryStats(categoryTransactions, 'expense').toFixed(2)} ₽
                  </p>
                </div>
                <div className="bg-green-50 rounded-xl p-3">
                  <p className="text-xs text-gray-600">Доходы</p>
                  <p className="text-lg font-bold text-secondary">
                    +{calculateCategoryStats(categoryTransactions, 'income').toFixed(2)} ₽
                  </p>
                </div>
              </div>
            </div>

            {/* Transactions List */}
            <div className="flex-1 overflow-y-auto p-6">
              {categoryTransactions.length === 0 ? (
                <div className="text-center py-8">
                  <i className="fas fa-receipt text-gray-300 text-5xl mb-3"></i>
                  <p className="text-gray-500">Нет транзакций в этой категории</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {categoryTransactions.map((tx) => (
                    <div
                      key={tx.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            tx.type === 'expense' ? 'bg-red-100' : 'bg-green-100'
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
                          <p className="text-xs text-gray-500">
                            {new Date(tx.date).toLocaleDateString('ru-RU', {
                              day: 'numeric',
                              month: 'long',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
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
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CategoryCard({ category, onEdit, onViewTransactions, deletePendingId, onDeleteClick }) {
  const isPending = deletePendingId === category.id;
  const isSystem = category.is_system;
  
  return (
    <div
      className="bg-white rounded-2xl shadow-sm p-4 border-l-4 hover:shadow-md transition cursor-pointer"
      style={{ borderColor: category.color }}
      onClick={() => onViewTransactions(category)}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: `${category.color}20` }}
          >
            <i
              className={`fas fa-${category.icon || 'tag'}`}
              style={{ color: category.color }}
            ></i>
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-bold text-gray-900 truncate">{category.name}</h3>
            <p className="text-sm text-gray-500">
              {category.type === 'expense' ? 'Расход' : 'Доход'}
            </p>
            {category.transactions_count !== undefined && (
              <p className="text-xs text-gray-400 mt-1">
                <i className="fas fa-receipt mr-1"></i>
                {category.transactions_count} транзакций
              </p>
            )}
            {isSystem && (
              <p className="text-xs text-gray-400 mt-1">
                <i className="fas fa-lock mr-1"></i>
                Системная
              </p>
            )}
          </div>
        </div>
        {!isSystem && (
          <div className="flex space-x-1 ml-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit(category);
              }}
              className={`p-2 rounded-lg transition ${
                isPending 
                  ? 'text-gray-400 hover:text-gray-500 bg-gray-100' 
                  : 'text-blue-600 hover:text-blue-800 hover:bg-blue-50'
              }`}
              title="Редактировать"
              disabled={isPending}
            >
              <i className="fas fa-edit"></i>
            </button>
            {isPending ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteClick(category.id);
                }}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg transition animate-pulse"
                title="Подтвердить удаление"
              >
                <i className="fas fa-check mr-1"></i>
                <span className="text-xs font-medium">OK</span>
              </button>
            ) : (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteClick(category.id);
                }}
                className="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded-lg transition"
                title="Удалить"
              >
                <i className="fas fa-trash"></i>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
