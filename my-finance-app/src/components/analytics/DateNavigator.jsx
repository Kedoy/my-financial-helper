export default function DateNavigator({ selectedDate, timePeriod, onNavigate, onToday, periodLabel }) {
  return (
    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
      <button
        type="button"
        onClick={() => onNavigate(-1)}
        className="p-2 hover:bg-gray-100 rounded-lg transition"
        title="Назад"
      >
        <i className="fas fa-chevron-left text-gray-600"></i>
      </button>
      <div className="flex items-center space-x-2">
        <button
          type="button"
          onClick={onToday}
          className="px-3 py-1.5 rounded-lg text-sm font-medium bg-primary text-white hover:bg-indigo-700 transition shadow"
          title="Выбрать сегодня"
        >
          <i className="fas fa-calendar-day mr-1"></i>
          Сегодня
        </button>
        <span className="font-medium text-gray-900">{periodLabel}</span>
      </div>
      <button
        type="button"
        onClick={() => onNavigate(1)}
        className="p-2 hover:bg-gray-100 rounded-lg transition"
        title="Вперёд"
      >
        <i className="fas fa-chevron-right text-gray-600"></i>
      </button>
    </div>
  );
}
