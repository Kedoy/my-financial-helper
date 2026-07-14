import { Pie } from 'react-chartjs-2';
import { ArcElement, Tooltip } from 'chart.js';
import { Chart as ChartJS } from 'chart.js';

ChartJS.register(ArcElement, Tooltip);

export default function CategoryPieChart({ 
  categoryStats, 
  visibleCategories, 
  onToggleCategory, 
  onToggleAll,
  onCategoryClick 
}) {
  if (!categoryStats?.by_category?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <i className="fas fa-chart-pie text-6xl mb-4 text-gray-300"></i>
        <p>Нет данных за выбранный период</p>
      </div>
    );
  }

  const visibleCategoriesCount = visibleCategories.size;
  const totalCategories = categoryStats.by_category.length;

  const filteredCategories = categoryStats.by_category.filter(
    c => visibleCategories.has(c.category)
  );

  const total = filteredCategories.reduce((sum, c) => sum + c.amount, 0);

  return (
    <>
      <div className="relative" style={{ height: '280px' }}>
        <Pie
          data={{
            labels: filteredCategories.map(c => c.category),
            datasets: [{
              data: filteredCategories.map(c => c.amount),
              backgroundColor: filteredCategories.map(c => c.color),
              borderWidth: 2,
              borderColor: '#fff',
            }],
          }}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: { size: 14 },
                bodyFont: { size: 13 },
                cornerRadius: 8,
                callbacks: {
                  label: (context) => {
                    const value = context.raw;
                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                    return `${context.label}: ${value.toFixed(2)} ₽ (${percentage}%)`;
                  }
                }
              }
            },
            onClick: (event, elements) => {
              if (elements.length > 0 && onCategoryClick) {
                const index = elements[0].index;
                const categoryName = filteredCategories[index].category;
                onCategoryClick(categoryName);
              }
            },
          }}
        />
      </div>

      <div className="mt-4 space-y-2 max-h-48 overflow-y-auto">
        {categoryStats.by_category.map((cat, index) => (
          <div
            key={index}
            onClick={() => onToggleCategory(cat.category)}
            className="flex items-center justify-between text-sm cursor-pointer hover:bg-gray-50 rounded px-2 py-1 transition"
          >
            <div className="flex items-center space-x-2">
              <div
                className={`w-3 h-3 rounded-full transition ${
                  visibleCategories.has(cat.category) ? '' : 'opacity-30 grayscale'
                }`}
                style={{ backgroundColor: cat.color }}
              ></div>
              <span className={`text-gray-700 truncate max-w-[150px] ${
                visibleCategories.has(cat.category) ? '' : 'line-through text-gray-400'
              }`}>{cat.category}</span>
            </div>
            <div className="text-right">
              <span className={`font-semibold ${
                visibleCategories.has(cat.category) ? 'text-gray-900' : 'text-gray-400'
              }`}>{cat.amount.toFixed(2)} ₽</span>
              <span className={`text-gray-500 ml-2 ${
                visibleCategories.has(cat.category) ? '' : 'text-gray-300'
              }`}>({cat.percentage}%)</span>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
