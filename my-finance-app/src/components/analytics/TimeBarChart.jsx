import { Bar } from 'react-chartjs-2';
import { CategoryScale, LinearScale, BarElement, Tooltip } from 'chart.js';
import { Chart as ChartJS } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

export default function TimeBarChart({ chartData, transactionType }) {
  if (!chartData || !chartData.data?.some(v => v > 0)) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <i className="fas fa-chart-bar text-6xl mb-4 text-gray-300"></i>
        <p>Нет данных за выбранный период</p>
      </div>
    );
  }

  const barColor = transactionType === 'expense' ? '#EF4444' : '#10B981';
  const label = transactionType === 'expense' ? 'Расходы' : 'Доходы';

  return (
    <div className="relative" style={{ height: '280px' }}>
      <Bar
        data={{
          labels: chartData.labels,
          datasets: [{
            label,
            data: chartData.data,
            backgroundColor: barColor,
            borderRadius: 6,
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
                label: (context) => `${context.raw.toFixed(2)} ₽`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f3f4f6' },
              ticks: {
                callback: (value) => `${value >= 1000 ? (value / 1000).toFixed(1) + 'k' : value}`,
                font: { size: 11 },
              },
            },
            x: {
              grid: { display: false },
              ticks: {
                font: { size: 10 },
                maxRotation: 45,
                minRotation: 45,
              },
            },
          },
        }}
      />
    </div>
  );
}
