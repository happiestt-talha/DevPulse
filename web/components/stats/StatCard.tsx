'use client';

import { motion } from 'framer-motion';

export function StatCard({ title, value, icon }: { title: string; value: string | number; icon?: React.ReactNode }) {
  return (
    <motion.div
      className="bg-surface rounded-xl border border-border p-4 flex flex-col gap-1"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm text-textSecondary">{title}</p>
        {icon && <span className="text-primary">{icon}</span>}
      </div>
      <p className="text-2xl font-bold font-mono text-textPrimary">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
    </motion.div>
  );
}
