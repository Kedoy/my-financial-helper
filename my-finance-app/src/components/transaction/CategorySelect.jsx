export default function CategorySelect({ value, categories, onCreateNew, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Категория
      </label>
      <select
        value={value}
        onChange={(e) => {
          if (e.target.value === 'new') {
            onCreateNew();
          } else {
            onChange(e.target.value);
          }
        }}
        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent"
      >
        <option value="">Без категории</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
        <option value="new" className="font-semibold text-primary">
          + Создать новую категорию
        </option>
      </select>
    </div>
  );
}
