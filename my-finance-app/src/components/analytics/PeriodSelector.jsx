export default function PeriodSelector({ value, onChange }) {
  const periods = [
    { value: 'day', label: 'День', icon: 'fa-sun' },
    { value: 'week', label: 'Неделя', icon: 'fa-calendar-week' },
    { value: 'month', label: 'Месяц', icon: 'fa-calendar' }
  ];

  return (
    <div className="flex space-x-2">
      {periods.map((period) => (
        <button
          key={period.value}
          onClick={() => onChange(period.value)}
          className={`flex-1 py-2.5 px-4 rounded-xl font-medium transition flex items-center justify-center ${
            value === period.value
              ? 'bg-primary text-white shadow-lg shadow-primary/30'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <i className={`fas ${period.icon} mr-2`}></i>
          {period.label}
        </button>
      ))}
    </div>
  );
}
