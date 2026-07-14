import { useState } from 'react';

export default function CustomCalendar({ value, onChange, transactionDates }) {
  const [currentDate, setCurrentDate] = useState(new Date(value || new Date()));
  const [selectedTime, setSelectedTime] = useState(
    value ? value.slice(11, 16) : (() => {
      const now = new Date();
      const moscowTime = new Date(now.toLocaleString('en-US', { timeZone: 'Europe/Moscow' }));
      return `${String(moscowTime.getHours()).padStart(2, '0')}:${String(moscowTime.getMinutes()).padStart(2, '0')}`;
    })()
  );

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();

  const MONTH_NAMES = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];

  const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  function formatDate(year, month, day) {
    const m = (month + 1).toString().padStart(2, '0');
    const d = day.toString().padStart(2, '0');
    return `${year}-${m}-${d}T${selectedTime}`;
  }

  function isToday(dateStr) {
    return dateStr === new Date().toISOString().split('T')[0];
  }

  function isFuture(dateStr) {
    return dateStr > new Date().toISOString().split('T')[0];
  }

  function hasTransactions(dateStr) {
    return transactionDates.includes(dateStr);
  }

  function goToPreviousMonth() {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  }

  function goToNextMonth() {
    const nextMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
    const today = new Date();
    const todayMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    if (nextMonth <= todayMonth) {
      setCurrentDate(nextMonth);
    }
  }

  function handleDateSelect(day) {
    const dateStr = formatDate(currentDate.getFullYear(), currentDate.getMonth(), day);
    if (!isFuture(dateStr)) {
      onChange(dateStr);
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <button
          type="button"
          onClick={goToPreviousMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <i className="fas fa-chevron-left text-gray-600"></i>
        </button>
        <span className="font-bold text-gray-900">
          {MONTH_NAMES[currentDate.getMonth()]} {currentDate.getFullYear()}
        </span>
        <button
          type="button"
          onClick={goToNextMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <i className="fas fa-chevron-right text-gray-600"></i>
        </button>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {WEEKDAYS.map((day) => (
          <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {Array(firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1)
          .fill(null)
          .map((_, i) => (
            <div key={`empty-${i}`} className="aspect-square"></div>
          ))}

        {Array(daysInMonth)
          .fill(null)
          .map((_, i) => {
            const day = i + 1;
            const dateStr = formatDate(currentDate.getFullYear(), currentDate.getMonth(), day);
            const dateOnly = dateStr.split('T')[0];
            const future = isFuture(dateOnly);
            const hasTx = hasTransactions(dateOnly);
            const isTodayDate = isToday(dateOnly);
            const selectedDate = value ? value.split('T')[0] : null;
            const isSelected = selectedDate === dateOnly;

            return (
              <button
                key={day}
                type="button"
                onClick={() => handleDateSelect(day)}
                disabled={future}
                className={`
                  aspect-square rounded-lg text-sm font-medium transition relative
                  ${future
                    ? 'bg-gray-100 text-gray-300 cursor-not-allowed line-through'
                    : ''
                  }
                  ${!future && isSelected
                    ? 'bg-primary text-white hover:bg-indigo-700'
                    : ''
                  }
                  ${!future && !isSelected && hasTx
                    ? 'bg-green-100 text-gray-900 hover:bg-green-200 border-2 border-green-300'
                    : ''
                  }
                  ${!future && !isSelected && !hasTx && !isTodayDate
                    ? 'bg-gray-50 text-gray-700 hover:bg-gray-100 border border-gray-200'
                    : ''
                  }
                  ${!future && !isSelected && isTodayDate && !hasTx
                    ? 'bg-blue-50 text-blue-700 hover:bg-blue-100 border-2 border-blue-300'
                    : ''
                  }
                  ${!future && !isSelected && isTodayDate && hasTx
                    ? 'bg-gradient-to-br from-green-100 to-blue-50 text-gray-900 hover:from-green-200 hover:to-blue-100 border-2 border-green-400'
                    : ''
                  }
                `}
              >
                {day}
                {hasTx && !isSelected && (
                  <span className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-green-500 rounded-full"></span>
                )}
              </button>
            );
          })}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <label className="block text-xs font-medium text-gray-600 mb-2">
          Время (МСК, 24ч)
        </label>
        <div className="flex gap-2">
          <select
            value={selectedTime.split(':')[0]}
            onChange={(e) => {
              const hours = e.target.value.padStart(2, '0');
              const minutes = selectedTime.split(':')[1] || '00';
              setSelectedTime(`${hours}:${minutes}`);
            }}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
          >
            {Array.from({ length: 24 }, (_, i) => i).map((hour) => (
              <option key={hour} value={hour.toString().padStart(2, '0')}>
                {hour.toString().padStart(2, '0')}
              </option>
            ))}
          </select>
          <span className="flex items-center text-lg font-bold text-gray-600">:</span>
          <select
            value={selectedTime.split(':')[1] || '00'}
            onChange={(e) => {
              const hours = selectedTime.split(':')[0] || '00';
              const minutes = e.target.value.padStart(2, '0');
              setSelectedTime(`${hours}:${minutes}`);
            }}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
          >
            {Array.from({ length: 60 }, (_, i) => i).map((minute) => (
              <option key={minute} value={minute.toString().padStart(2, '0')}>
                {minute.toString().padStart(2, '0')}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="button"
        onClick={() => {
          const now = new Date();
          const dateStr = formatDate(now.getFullYear(), now.getMonth(), now.getDate());
          onChange(dateStr);
        }}
        className="mt-3 w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition"
      >
        <i className="fas fa-calendar-day mr-2"></i>
        Сегодня
      </button>
    </div>
  );
}
