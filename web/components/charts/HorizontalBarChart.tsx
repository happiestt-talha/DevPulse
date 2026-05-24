'use client';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export function HorizontalBarChart({ data, title, barColor = '#7C3AED' }: { data: any[]; title: string; barColor?: string }) {
  if (!data.length) return null;
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <ResponsiveContainer width="100%" height={Math.max(200, data.length * 30)}>
        <BarChart layout="vertical" data={data} margin={{ left: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2D2A63" />
          <XAxis type="number" stroke="#94A3B8" />
          <YAxis type="category" dataKey="name" stroke="#94A3B8" />
          <Tooltip contentStyle={{ backgroundColor: '#1E1B4B', border: '1px solid #3B3980' }} />
          <Bar dataKey="value" fill={barColor} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}