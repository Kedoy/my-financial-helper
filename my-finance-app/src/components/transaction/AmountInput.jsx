export default function AmountInput({ value, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Сумма (₽)
      </label>
      <input
        type="number"
        step="0.01"
        min="0"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent text-lg"
        placeholder="0.00"
      />
    </div>
  );
}
