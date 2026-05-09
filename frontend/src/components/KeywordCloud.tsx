import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useTheme } from '../hooks/useTheme'

interface KeywordItem {
  text: string
  value: number
}

interface KeywordCloudProps {
  keywords: KeywordItem[]
  className?: string
}

export default function KeywordCloud({ keywords, className = '' }: KeywordCloudProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const [width, setWidth] = useState(600)
  const { isDark } = useTheme()
  const HEIGHT = 320

  // Measure container width with ResizeObserver
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(entries => {
      const w = entries[0]?.contentRect.width
      if (w) setWidth(w)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!keywords || keywords.length === 0 || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    // Build hierarchy
    const root = d3.hierarchy({ children: keywords } as any)
      .sum((d: any) => d.value || 0)
      .sort((a, b) => (b.value || 0) - (a.value || 0))

    // Compute treemap layout
    d3.treemap<any>()
      .size([width, HEIGHT])
      .tile(d3.treemapSquarify)
      .paddingInner(0)
      .paddingOuter(0)
      (root)

    const leaves = root.leaves()
    const maxVal = d3.max(leaves, d => d.value || 0) || 1

    const borderColor = isDark ? '#1f2937' : '#e5e7eb'

    // Tooltip
    const tooltip = d3.select('body').append('div')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', isDark ? '#1a1a1a' : '#ffffff')
      .style('border', `1px solid ${isDark ? '#333' : '#e5e7eb'}`)
      .style('padding', '8px 12px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('color', isDark ? '#ffffff' : '#111827')
      .style('pointer-events', 'none')
      .style('z-index', '9999')
      .style('box-shadow', '0 2px 8px rgba(0,0,0,0.15)')

    const cell = svg.selectAll('g')
      .data(leaves)
      .join('g')
      .attr('transform', d => `translate(${(d as any).x0},${(d as any).y0})`)

    // Hit area rect (mouse events only, no stroke)
    cell.append('rect')
      .attr('width', d => Math.max(0, (d as any).x1 - (d as any).x0))
      .attr('height', d => Math.max(0, (d as any).y1 - (d as any).y0))
      .attr('fill', 'transparent')
      .attr('stroke', 'none')
      .style('cursor', 'default')
      .on('mouseover', function (_event, d) {
        d3.select(this).attr('fill', isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)')
        tooltip
          .style('visibility', 'visible')
          .html(`<strong>${(d.data as any).text}</strong><br/>언급 횟수: ${(d.value || 0).toLocaleString()}회`)
      })
      .on('mousemove', function (event) {
        tooltip
          .style('top', (event.pageY - 10) + 'px')
          .style('left', (event.pageX + 10) + 'px')
      })
      .on('mouseout', function () {
        d3.select(this).attr('fill', 'transparent')
        tooltip.style('visibility', 'hidden')
      })

    // Right border line
    cell.append('line')
      .attr('x1', d => (d as any).x1 - (d as any).x0)
      .attr('y1', 0)
      .attr('x2', d => (d as any).x1 - (d as any).x0)
      .attr('y2', d => (d as any).y1 - (d as any).y0)
      .attr('stroke', borderColor)
      .attr('stroke-width', 1)
      .style('pointer-events', 'none')

    // Bottom border line
    cell.append('line')
      .attr('x1', 0)
      .attr('y1', d => (d as any).y1 - (d as any).y0)
      .attr('x2', d => (d as any).x1 - (d as any).x0)
      .attr('y2', d => (d as any).y1 - (d as any).y0)
      .attr('stroke', borderColor)
      .attr('stroke-width', 1)
      .style('pointer-events', 'none')

    // Keyword label
    cell.append('text')
      .attr('x', d => ((d as any).x1 - (d as any).x0) / 2)
      .attr('y', d => {
        const h = (d as any).y1 - (d as any).y0
        return h / 2 - 5
      })
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .style('font-size', d => {
        const w = (d as any).x1 - (d as any).x0
        const h = (d as any).y1 - (d as any).y0
        return `${Math.min(w / 5, h / 3, 14)}px`
      })
      .style('fill', isDark ? '#f3f4f6' : '#1f2937')
      .style('font-weight', '600')
      .style('pointer-events', 'none')
      .style('opacity', d => {
        const w = (d as any).x1 - (d as any).x0
        const h = (d as any).y1 - (d as any).y0
        return w < 40 || h < 30 ? 0 : 1
      })
      .text(d => (d.data as any).text)

    // Count label below keyword
    cell.append('text')
      .attr('x', d => ((d as any).x1 - (d as any).x0) / 2)
      .attr('y', d => {
        const h = (d as any).y1 - (d as any).y0
        return h / 2 + 10
      })
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '10px')
      .style('fill', isDark ? '#9ca3af' : '#6b7280')
      .style('pointer-events', 'none')
      .style('opacity', d => {
        const w = (d as any).x1 - (d as any).x0
        const h = (d as any).y1 - (d as any).y0
        return w < 50 || h < 45 ? 0 : 1
      })
      .text(d => (d.value || 0).toLocaleString())

    return () => {
      tooltip.remove()
    }
  }, [keywords, width, isDark])

  if (!keywords || keywords.length === 0) {
    return (
      <div className="keyword-cloud--empty" data-component="keyword-cloud" data-state="empty">
        <p className="text-sm text-gray-400 text-center">키워드 데이터가 없습니다</p>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className={`keyword-cloud ${className}`}
      data-component="keyword-cloud"
    >
      <svg
        ref={svgRef}
        viewBox={`0 0 ${width} ${HEIGHT}`}
        preserveAspectRatio="none"
        style={{ display: 'block', width: '100%', height: HEIGHT, overflow: 'hidden' }}
      />
    </div>
  )
}
