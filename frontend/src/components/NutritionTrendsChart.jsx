import React from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const nutrientLines = [
  { key: 'protein', label: 'Protein', color: '#2563eb' },
  { key: 'carbs', label: 'Carbs', color: '#f59e0b' },
  { key: 'fats', label: 'Fats', color: '#e11d48' },
];

function NutritionTrendsChart({ data = [] }) {
  const hasLoggedMacros = data.some((day) =>
    nutrientLines.some(({ key }) => Number(day[key]) > 0)
  );

  return (
    <section
      className="w-full bg-white rounded-[28px] p-5 sm:p-6 mb-4 shadow-xs border border-gray-100/60"
      aria-label="Weekly nutrition trends"
    >
      <div className="mb-4">
        <h3 className="text-[18px] font-bold text-gray-900 tracking-tight">Nutrition Trends</h3>
        <p className="text-[12px] text-gray-400 font-medium mt-0.5">Protein, carbs and fats logged this week</p>
      </div>

      {hasLoggedMacros ? (
        <div className="h-[230px] w-full" role="img" aria-label="Line chart comparing daily protein, carbs and fats in grams">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 8, right: 10, left: -18, bottom: 0 }}>
              <CartesianGrid stroke="#eef0f3" strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="day"
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                dy={8}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                width={38}
                label={{ value: 'grams', angle: -90, position: 'insideLeft', fill: '#9ca3af', fontSize: 10 }}
              />
              <Tooltip
                formatter={(value, name) => [`${value} g`, name]}
                contentStyle={{ borderRadius: 12, borderColor: '#e5e7eb', fontSize: 12 }}
              />
              <Legend
                verticalAlign="top"
                align="right"
                iconType="circle"
                iconSize={7}
                wrapperStyle={{ fontSize: 11, paddingBottom: 12 }}
              />
              {nutrientLines.map(({ key, label, color }) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  name={label}
                  stroke={color}
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: color, strokeWidth: 0 }}
                  activeDot={{ r: 5, strokeWidth: 0 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-[190px] flex items-center justify-center rounded-2xl bg-gray-50 px-6 text-center">
          <p className="text-sm text-gray-500">Log a meal to see your protein, carbs and fats trends here.</p>
        </div>
      )}
    </section>
  );
}

export default NutritionTrendsChart;
