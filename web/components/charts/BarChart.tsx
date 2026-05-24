'use client';

import { BarChart as ReBarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export function BarChart({ data, title }: { data: any[]; title: string }) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <ResponsiveContainer width="100%" height={200}>
        <ReBarChart data={data}>
          <XAxis dataKey="name" stroke="#94A3B8" />
          <YAxis stroke="#94A3B8" />
          <Tooltip />
          <Bar dataKey="value" fill="#7C3AED" />
        </ReBarChart>
      </ResponsiveContainer>
    </div>
  );
}