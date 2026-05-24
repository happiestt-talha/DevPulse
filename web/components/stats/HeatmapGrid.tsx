'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useGitHubStats } from '@/lib/api';

export function HeatmapGrid() {
  const svgRef = useRef<SVGSVGElement>(null);
  const { data: stats } = useGitHubStats();

  useEffect(() => {
    if (!stats || !svgRef.current) return;
    const contributions = stats.contribution_data || [];
    const width = 800;
    const height = 120;
    const cellSize = 12;
    const margin = { top: 20, right: 20, bottom: 20, left: 40 };

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const colorScale = d3.scaleSequentialLog()
      .domain([1, d3.max(contributions, (d) => d.count) || 1])
      .interpolator(d3.interpolateRgb('#1E1B4B', '#7C3AED'));

    const groups: Record<string, number[]> = {};
    contributions.forEach((d) => {
      const date = new Date(d.date);
      const week = d3.timeFormat('%Y-%U')(date);
      const day = date.getDay();
      if (!groups[week]) groups[week] = new Array(7).fill(0);
      groups[week][day] = d.count;
    });

    const weeks = Object.keys(groups);
    weeks.forEach((week, col) => {
      for (let row = 0; row < 7; row++) {
        const count = groups[week][row] || 0;
        svg
          .append('rect')
          .attr('x', margin.left + col * cellSize)
          .attr('y', margin.top + row * cellSize)
          .attr('width', cellSize - 1)
          .attr('height', cellSize - 1)
          .attr('rx', 2)
          .attr('fill', count > 0 ? colorScale(count) : '#2D2A63')
          .append('title')
          .text(`Week ${week}, day ${row}: ${count} contributions`);
      }
    });
  }, [stats]);

  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-lg font-semibold mb-2">Contribution Heatmap</h3>
      <svg
        ref={svgRef}
        width="100%"
        height="140"
        viewBox="0 0 800 140"
        preserveAspectRatio="xMidYMid meet"
      />
    </div>
  );
}
