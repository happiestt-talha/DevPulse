'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useGitHubStats } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';

export function HeatmapGrid() {
  const svgRef = useRef<SVGSVGElement>(null);
  const { data: stats, isLoading } = useGitHubStats();

  useEffect(() => {
    if (isLoading || !stats?.contribution_data || !svgRef.current) return;

    const contributions = stats.contribution_data;
    const width = 800;
    const height = 140;
    const cellSize = 12;
    const margin = { top: 20, right: 20, bottom: 20, left: 40 };

    // Clear previous
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Group by week (year-week number) and day of week (0=Sunday)
    const weeksMap: Record<string, number[]> = {};
    contributions.forEach((d: { date: string; count: number }) => {
      const date = new Date(d.date);
      const year = date.getFullYear();
      const weekNum = d3.timeFormat('%U')(date);
      const weekKey = `${year}-${weekNum}`;
      const day = date.getDay(); // 0=Sunday
      if (!weeksMap[weekKey]) weeksMap[weekKey] = new Array(7).fill(0);
      weeksMap[weekKey][day] = d.count;
    });

    const weeks = Object.keys(weeksMap).sort();
    const maxCount = d3.max(contributions, (d: { count: number }) => d.count) || 1;
    const colorScale = d3.scaleSequentialLog()
      .domain([1, maxCount])
      .interpolator(d3.interpolateRgb('#2D2A63', '#7C3AED'));

    // Draw cells
    weeks.forEach((week, col) => {
      for (let row = 0; row < 7; row++) {
        const count = weeksMap[week][row] || 0;
        svg.append('rect')
          .attr('x', margin.left + col * cellSize)
          .attr('y', margin.top + row * cellSize)
          .attr('width', cellSize - 1)
          .attr('height', cellSize - 1)
          .attr('fill', count > 0 ? colorScale(count) : '#1E1B4B')
          .attr('rx', 2)
          .append('title')
          .text(`Week ${week}, day ${row}: ${count} contributions`);
      }
    });

    // Add month labels (simplified)
    const months = d3.timeMonths(new Date(contributions[0]?.date), new Date(contributions[contributions.length - 1]?.date));
    months.forEach((month, i) => {
      const firstDayOfMonth = new Date(month.getFullYear(), month.getMonth(), 1);
      const weekOfMonth = d3.timeFormat('%U')(firstDayOfMonth);
      const weekKey = `${firstDayOfMonth.getFullYear()}-${weekOfMonth}`;
      const col = weeks.indexOf(weekKey);
      if (col !== -1) {
        svg.append('text')
          .attr('x', margin.left + col * cellSize + cellSize / 2)
          .attr('y', margin.top - 5)
          .attr('text-anchor', 'middle')
          .style('font-size', '10px')
          .style('fill', '#94A3B8')
          .text(d3.timeFormat('%b')(month));
      }
    });
  }, [stats, isLoading]);

  if (isLoading) return <Skeleton className="h-40 w-full" />;
  if (!stats) return <div className="text-textSecondary text-center p-4">No contribution data</div>;

  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-sm font-medium text-textSecondary mb-2">Contribution Activity</h3>
      <svg ref={svgRef} width="100%" height="140" viewBox="0 0 800 140" preserveAspectRatio="xMidYMid meet"></svg>
      <div className="flex justify-end mt-2 text-xs text-textSecondary">
        <span>Less</span>
        <div className="w-3 h-3 bg-[#2D2A63] mx-1"></div>
        <div className="w-3 h-3 bg-primary mx-1"></div>
        <span>More</span>
      </div>
    </div>
  );
}