export default function TransactionTypeTabs({ value, onChange }) {
  const tabs = [
    { value: 'expense', label: 'Расходы', color: 'text-danger', bg: 'bg-red-50', icon: 'fa-arrow-down' },
    { value: 'income', label: 'Доходы', color: 'text-secondary', bg: 'bg-green-50', icon: 'fa-arrow-up' }
  ];

  return (
    <div className="flex space-x-2">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={`flex-1 py-2.5 px-4 rounded-xl font-medium transition ${
            value === tab.value
              ? `${tab.bg} ${tab.color} ring-2 ring-offset-1 ${
                  tab.value === 'expense' ? 'ring-red-200' : 'ring-green-200'
                }`
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <i className={`fas ${tab.icon} mr-2`}></i>
          {tab.label}
        </button>
      ))}
    </div>
  );
}
