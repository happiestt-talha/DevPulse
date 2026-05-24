'use client';

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#7C3AED', '#06B6D4', '#F59E0B', '#10B981', '#EF4444'];

export function DonutChart({ data, title }: { data: any[]; title: string }) {
  if (!data || data.length === 0) return null;
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie data={data} dataKey="percent" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} fill="#7C3AED">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}