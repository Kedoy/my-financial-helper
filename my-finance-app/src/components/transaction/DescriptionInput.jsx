export default function DescriptionInput({ value, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Описание (необязательно)
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
        placeholder="Например: Продукты в магазине"
      />
    </div>
  );
}
