export default function SummaryCards({ summary, transactionType, periodLabel }) {
  if (!summary) return null;

  const average = summary.count > 0 
    ? (summary.total / summary.count).toFixed(2) 
    : '0';

  const amountColor = transactionType === 'expense' ? 'text-danger' : 'text-secondary';

  return (
    <div className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl p-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-gray-600 text-sm font-medium">Всего</p>
          <p className={`text-2xl font-bold mt-1 ${amountColor}`}>
            {summary.total.toFixed(2)} ₽
          </p>
        </div>
        <div>
          <p className="text-gray-600 text-sm font-medium">Транзакций</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{summary.count}</p>
        </div>
        <div>
          <p className="text-gray-600 text-sm font-medium">Среднее</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {average} ₽
          </p>
        </div>
        <div>
          <p className="text-gray-600 text-sm font-medium">Период</p>
          <p className="text-lg font-bold text-gray-900 mt-1 truncate" title={periodLabel}>
            {periodLabel}
          </p>
        </div>
      </div>
    </div>
  );
}
