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

function getTextColor(isDark: boolean): string {
  return isDark ? '#f3f4f6' : '#1f2937'
}

function getCountColor(isDark: boolean): string {
  return isDark ? '#4b5563' : '#d1d5db'
}

export default function KeywordCloud({ keywords, className = '' }: KeywordCloudProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const [width, setWidth] = useState(600)
  const { isDark } = useTheme()
  const HEIGHT = 280

  // Fix 1: debounce timer ref
  const resizeTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Fix 2: tooltip singleton ref
  const tooltipRef = useRef<d3.Selection<HTMLDivElement, unknown, HTMLElement, any> | null>(null)

  // Fix 3: track previous keywords to detect resize-only updates
  const prevKeywordsRef = useRef(keywords)

  // Fix 1: debounced ResizeObserver
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(entries => {
      const w = entries[0]?.contentRect.width
      if (!w) return
      if (resizeTimer.current) clearTimeout(resizeTimer.current)
      resizeTimer.current = setTimeout(() => setWidth(w), 150)
    })
    observer.observe(el)
    return () => {
      observer.disconnect()
      if (resizeTimer.current) clearTimeout(resizeTimer.current)
    }
  }, [])

  // Fix 2: tooltip created once per theme, not per render
  useEffect(() => {
    tooltipRef.current = d3.select('body').append('div')
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

    return () => { tooltipRef.current?.remove() }
  }, [isDark])

  useEffect(() => {
    if (!keywords || keywords.length === 0 || !svgRef.current) return

    // Fix 3: detect if only width changed (resize) vs keyword data changed
    const isResizeOnly = prevKeywordsRef.current === keywords
    prevKeywordsRef.current = keywords

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const root = d3.hierarchy({ children: keywords } as any)
      .sum((d: any) => d.value || 0)
      .sort((a, b) => (b.value || 0) - (a.value || 0))

    d3.treemap<any>()
      .size([width, HEIGHT])
      .tile(d3.treemapSquarify)
      .paddingInner(1)
      .paddingOuter(0)
      (root)

    const leaves = root.leaves()
    const maxVal = d3.max(leaves, d => d.value || 0) || 1

    // Fix 2: reuse tooltip from ref
    const tooltip = tooltipRef.current

    // Fix 3: animate only when keyword data changes, skip on resize
    const cellBase = svg.selectAll('g')
      .data(leaves)
      .join('g')
      .attr('transform', d => `translate(${(d as any).x0},${(d as any).y0})`)

    if (isResizeOnly) {
      cellBase.style('opacity', 1)
    } else {
      cellBase.style('opacity', 0)
        .transition()
        .duration(400)
        .delay((_d, i) => i * 30)
        .style('opacity', 1)
    }

    const cellGroup = svg.selectAll('g')

    const cellW = (d: any) => Math.max(0, d.x1 - d.x0)
    const cellH = (d: any) => Math.max(0, d.y1 - d.y0)

    const borderColor = isDark ? '#374151' : '#e5e7eb'

    // Background fill (inverted for top keyword at index 0)
    cellGroup.append('rect')
      .attr('width', d => cellW(d))
      .attr('height', d => cellH(d))
      .attr('fill', (_d, i) => i === 0 ? (isDark ? '#f3f4f6' : '#1f2937') : 'transparent')
      .attr('stroke', 'none')
      .style('pointer-events', 'none')

    // Right border line
    cellGroup.append('line')
      .attr('x1', d => cellW(d))
      .attr('y1', 0)
      .attr('x2', d => cellW(d))
      .attr('y2', d => cellH(d))
      .attr('stroke', borderColor)
      .attr('stroke-width', 1)
      .style('pointer-events', 'none')

    // Bottom border line
    cellGroup.append('line')
      .attr('x1', 0)
      .attr('y1', d => cellH(d))
      .attr('x2', d => cellW(d))
      .attr('y2', d => cellH(d))
      .attr('stroke', borderColor)
      .attr('stroke-width', 1)
      .style('pointer-events', 'none')

    // Hit area (hover effect)
    cellGroup.append('rect')
      .attr('width', d => cellW(d))
      .attr('height', d => cellH(d))
      .attr('fill', 'transparent')
      .attr('stroke', 'none')
      .style('cursor', 'default')
      .on('mouseover', function (_event, d) {
        // Fix 4: direct style change, no transition
        svg.selectAll('g').style('opacity', 0.3)
        d3.select((this as any).parentNode).style('opacity', 1)
        d3.select(this).attr('fill', isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)')
        if (tooltip) {
          tooltip
            .style('visibility', 'visible')
            .html(`<strong>${(d.data as any).text}</strong><br/>언급 횟수: ${(d.value || 0).toLocaleString()}회`)
        }
      })
      .on('mousemove', function (event) {
        if (tooltip) {
          tooltip
            .style('top', (event.pageY - 10) + 'px')
            .style('left', (event.pageX + 10) + 'px')
        }
      })
      .on('mouseout', function () {
        // Fix 4: direct style change, no transition
        svg.selectAll('g').style('opacity', 1)
        d3.select(this).attr('fill', 'transparent')
        if (tooltip) tooltip.style('visibility', 'hidden')
      })

    // Count label (top-left)
    cellGroup.append('text')
      .attr('x', 6)
      .attr('y', 14)
      .attr('text-anchor', 'start')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '10px')
      .style('fill', (_d, i) => i === 0 ? (isDark ? '#6b7280' : '#9ca3af') : getCountColor(isDark))
      .style('pointer-events', 'none')
      .style('opacity', d => (cellW(d) < 40 || cellH(d) < 30 ? 0 : 1))
      .text(d => (d.value || 0).toLocaleString())

    // Block bar indicator (bottom-right)
    cellGroup.append('text')
      .attr('x', d => cellW(d) - 6)
      .attr('y', d => cellH(d) - 8)
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '14px')
      .style('fill', (_d, i) => i === 0 ? (isDark ? '#6b7280' : '#9ca3af') : (isDark ? '#9ca3af' : '#9E9E9E'))
      .style('pointer-events', 'none')
      .style('opacity', d => (cellW(d) < 50 || cellH(d) < 35 ? 0 : 1))
      .text(d => {
        const t = (d.value || 0) / maxVal
        const filled = Math.round(t * 5)
        return '▪'.repeat(filled) + '▫'.repeat(5 - filled)
      })

    // Keyword label
    cellGroup.append('text')
      .attr('x', d => cellW(d) / 2)
      .attr('y', d => {
        const h = cellH(d)
        return h / 2 - 5
      })
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .style('font-size', d => {
        const w = cellW(d)
        const h = cellH(d)
        const t = (d.value || 0) / maxVal
        const freqSize = 10 + t * 14  // 10px ~ 24px
        return `${Math.min(w / 4, h / 2.5, freqSize)}px`
      })
      .style('fill', (_d, i) => i === 0 ? (isDark ? '#1f2937' : '#f3f4f6') : getTextColor(isDark))
      .style('font-weight', '600')
      .style('pointer-events', 'none')
      .style('opacity', d => (cellW(d) < 40 || cellH(d) < 30 ? 0 : 1))
      .text(d => (d.data as any).text)

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
