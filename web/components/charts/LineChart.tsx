'use client';

import { LineChart as ReLineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export function LineChart({ data, xKey, yKey, title, color = '#06B6D4' }: { data: any[]; xKey: string; yKey: string; title?: string; color?: string }) {
  if (!data.length) return null;
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
      <ResponsiveContainer width="100%" height={200}>
        <ReLineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2D2A63" />
          <XAxis dataKey={xKey} stroke="#94A3B8" tick={{ fontSize: 12 }} />
          <YAxis stroke="#94A3B8" tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: '#1E1B4B', border: '1px solid #3B3980' }} />
          <Line type="monotone" dataKey={yKey} stroke={color} strokeWidth={2} dot={{ r: 3 }} />
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  );
}