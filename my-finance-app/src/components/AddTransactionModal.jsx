import { useState, useEffect } from 'react';
import { transactionsAPI, categoriesAPI } from '../api';
import TransactionTypeSelector from './transaction/TransactionTypeSelector';
import AmountInput from './transaction/AmountInput';
import CategorySelect from './transaction/CategorySelect';
import DescriptionInput from './transaction/DescriptionInput';
import DateTimeField from './transaction/DateTimeField';
import CategoryModal from './transaction/CategoryModal';

export default function AddTransactionModal({ isOpen, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [transactionDates, setTransactionDates] = useState([]);
  const [categoryFormData, setCategoryFormData] = useState({
    name: '',
    type: 'expense',
    icon: 'shopping_cart',
    color: '#4F46E5',
  });

  const [formData, setFormData] = useState({
    type: 'expense',
    amount: '',
    category: '',
    description: '',
    date: new Date().toISOString().slice(0, 16),
  });

  useEffect(() => {
    if (isOpen) {
      loadCategories();
      loadTransactionDates();
    }
  }, [isOpen]);

  async function loadCategories() {
    try {
      const response = await categoriesAPI.list();
      setCategories(response.data.results || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  }

  async function loadTransactionDates() {
    try {
      const response = await transactionsAPI.list();
      const dates = (response.data.results || []).map(tx =>
        new Date(tx.date).toISOString().split('T')[0]
      );
      setTransactionDates([...new Set(dates)]);
    } catch (error) {
      console.error('Error loading transaction dates:', error);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const data = {
        type: formData.type,
        amount: parseFloat(formData.amount),
        description: formData.description || null,
        date: new Date(formData.date).toISOString(),
      };

      if (formData.category) {
        data.category = parseInt(formData.category);
      }

      await transactionsAPI.create(data);
      onSuccess();
      onClose();
      resetForm();
    } catch (error) {
      console.error('Error creating transaction:', error);
      alert('Ошибка при создании транзакции: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateCategory(data) {
    try {
      const response = await categoriesAPI.create(data);
      const newCategory = response.data;
      setCategories([...categories, newCategory]);
      setFormData({ ...formData, category: String(newCategory.id) });
      setShowCategoryModal(false);
      setCategoryFormData({
        name: '',
        type: 'expense',
        icon: 'shopping_cart',
        color: '#4F46E5',
      });
    } catch (error) {
      console.error('Error creating category:', error);
      const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message;
      alert('Ошибка при создании категории: ' + errorMsg);
    }
  }

  function resetForm() {
    setFormData({
      type: 'expense',
      amount: '',
      category: '',
      description: '',
      date: new Date().toISOString().slice(0, 16),
    });
  }

  function openCategoryModal() {
    setCategoryFormData({
      name: '',
      type: formData.type,
      icon: 'shopping_cart',
      color: '#4F46E5',
    });
    setShowCategoryModal(true);
  }

  if (!isOpen) return null;

  const filteredCategories = categories.filter(cat => cat.type === formData.type);

  return (
    <>
      <div
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        onClick={onClose}
      >
        <div
          className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 m-4 max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Новая транзакция</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <TransactionTypeSelector
              value={formData.type}
              onChange={(type) => setFormData({ ...formData, type, category: '' })}
            />

            <AmountInput
              value={formData.amount}
              onChange={(amount) => setFormData({ ...formData, amount })}
            />

            <CategorySelect
              value={formData.category}
              categories={filteredCategories}
              onCreateNew={openCategoryModal}
              onChange={(category) => setFormData({ ...formData, category })}
            />

            <DescriptionInput
              value={formData.description}
              onChange={(description) => setFormData({ ...formData, description })}
            />

            <DateTimeField
              value={formData.date}
              onChange={(date) => setFormData({ ...formData, date })}
              transactionDates={transactionDates}
            />

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
                    <span>Сохранить</span>
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

      <CategoryModal
        isOpen={showCategoryModal}
        onClose={() => setShowCategoryModal(false)}
        onSubmit={handleCreateCategory}
        loading={loading}
      />
    </>
  );
}
