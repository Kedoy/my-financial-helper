export default function TransactionTypeSelector({ value, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Тип операции
      </label>
      <div className="flex space-x-4">
        <label className="flex-1">
          <input
            type="radio"
            name="type"
            value="expense"
            checked={value === 'expense'}
            onChange={(e) => onChange(e.target.value)}
            className="peer sr-only"
          />
          <div className="flex items-center justify-center py-3 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-danger peer-checked:bg-red-50 peer-checked:text-danger transition">
            <i className="fas fa-arrow-down mr-2"></i>
            <span>Расход</span>
          </div>
        </label>
        <label className="flex-1">
          <input
            type="radio"
            name="type"
            value="income"
            checked={value === 'income'}
            onChange={(e) => onChange(e.target.value)}
            className="peer sr-only"
          />
          <div className="flex items-center justify-center py-3 px-4 border-2 border-gray-300 rounded-xl cursor-pointer peer-checked:border-secondary peer-checked:bg-green-50 peer-checked:text-secondary transition">
            <i className="fas fa-arrow-up mr-2"></i>
            <span>Доход</span>
          </div>
        </label>
      </div>
    </div>
  );
}
