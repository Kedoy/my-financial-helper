import { useState, useEffect, useRef } from 'react';
import CustomCalendar from './CustomCalendar';

export default function DateTimeField({ value, onChange, transactionDates }) {
  const [showCalendar, setShowCalendar] = useState(false);
  const calendarButtonRef = useRef(null);
  const [calendarPosition, setCalendarPosition] = useState({ top: 0, left: 0, width: 0 });

  useEffect(() => {
    if (!showCalendar) return;

    function handleClickOutside(event) {
      const calendarDropdown = calendarButtonRef.current?.parentElement?.querySelector('.calendar-dropdown');
      if (calendarDropdown && !calendarDropdown.contains(event.target)) {
        setShowCalendar(false);
      }
    }

    if (calendarButtonRef.current) {
      const button = calendarButtonRef.current;
      const rect = button.getBoundingClientRect();
      const calendarHeight = 350;
      const spaceAbove = rect.top;
      const positionTop = spaceAbove >= calendarHeight + 10
        ? rect.top - calendarHeight - 10
        : rect.bottom + 10;

      setCalendarPosition({
        top: positionTop,
        left: rect.left,
        width: rect.width
      });
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showCalendar]);

  function formatDateTime(dateStr) {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const datePart = date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
    const timePart = date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
    return `${datePart}, ${timePart}`;
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Дата и время
      </label>
      <div className="relative">
        <button
          type="button"
          ref={calendarButtonRef}
          onClick={() => setShowCalendar(!showCalendar)}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent text-left bg-white hover:bg-gray-50 transition flex items-center justify-between"
        >
          <span>
            {value ? formatDateTime(value) : (
              <span className="text-gray-500">Выберите дату</span>
            )}
          </span>
          <i className={`fas fa-chevron-${showCalendar ? 'up' : 'down'} text-gray-400`}></i>
        </button>

        {showCalendar && (
          <div
            className="calendar-dropdown fixed z-[100] bg-white rounded-xl shadow-2xl border border-gray-200 p-4"
            style={{
              top: `${calendarPosition.top}px`,
              left: `${calendarPosition.left}px`,
              width: `${calendarPosition.width}px`
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <CustomCalendar
              value={value}
              onChange={(date) => {
                onChange(date);
                setShowCalendar(false);
              }}
              transactionDates={transactionDates}
              onClose={() => setShowCalendar(false)}
            />
            <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-100 rounded border border-green-300"></div>
                <span>Есть транзакции</span>
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <div className="w-3 h-3 bg-gray-50 rounded border border-gray-200"></div>
                <span>Нет данных</span>
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <div className="w-3 h-3 bg-gray-100 rounded line-through"></div>
                <span>Недоступно (будущее)</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
