import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { useTheme } from '../hooks/useTheme'

interface KeywordItem {
    text: string
    value: number
}

interface SentimentBarChartProps {
    keywords: KeywordItem[]
    maxItems?: number
}

export default function SentimentBarChart({ keywords, maxItems = 10 }: SentimentBarChartProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const svgRef = useRef<SVGSVGElement>(null)
    const { isDark } = useTheme()

    useEffect(() => {
        if (!keywords || keywords.length === 0 || !svgRef.current || !containerRef.current) return

        const container = containerRef.current
        const svg = d3.select(svgRef.current)

        // Clear previous content
        svg.selectAll('*').remove()

        // Sort and limit data
        const sortedData = [...keywords]
            .sort((a, b) => b.value - a.value)
            .slice(0, maxItems)

        // Get container dimensions
        const { width: containerWidth } = container.getBoundingClientRect()
        const margin = { top: 10, right: 60, bottom: 10, left: 100 }
        const width = containerWidth - margin.left - margin.right
        const barHeight = 28
        const barGap = 8
        const height = sortedData.length * (barHeight + barGap) + margin.top + margin.bottom

        svg.attr('width', containerWidth).attr('height', height)

        // Create scales
        const xScale = d3.scaleLinear()
            .domain([0, d3.max(sortedData, d => d.value) || 1])
            .range([0, width])

        const yScale = d3.scaleBand()
            .domain(sortedData.map(d => d.text))
            .range([margin.top, height - margin.bottom])
            .padding(0.2)

        // Create gradient
        const gradient = svg.append('defs')
            .append('linearGradient')
            .attr('id', 'barGradient')
            .attr('x1', '0%')
            .attr('x2', '100%')

        if (isDark) {
            gradient.append('stop').attr('offset', '0%').attr('stop-color', '#525252')
            gradient.append('stop').attr('offset', '100%').attr('stop-color', '#737373')
        } else {
            gradient.append('stop').attr('offset', '0%').attr('stop-color', '#6b7280')
            gradient.append('stop').attr('offset', '100%').attr('stop-color', '#9ca3af')
        }

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},0)`)

        // Create tooltip
        const tooltip = d3.select('body').append('div')
            .attr('class', 'bar-tooltip')
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

        // Draw bars with animation
        g.selectAll('rect')
            .data(sortedData)
            .join('rect')
            .attr('x', 0)
            .attr('y', d => yScale(d.text) || 0)
            .attr('height', yScale.bandwidth())
            .attr('fill', 'url(#barGradient)')
            .attr('rx', 3)
            .attr('width', 0)
            .style('cursor', 'pointer')
            .transition()
            .duration(600)
            .delay((_, i) => i * 50)
            .ease(d3.easeQuadOut)
            .attr('width', d => xScale(d.value))

        // Add interactivity
        g.selectAll('rect')
            .on('mouseover', function (_event, d: any) {
                d3.select(this)
                    .transition()
                    .duration(150)
                    .attr('opacity', 0.8)

                tooltip
                    .style('visibility', 'visible')
                    .html(`<strong>${d.text}</strong><br/>언급 횟수: ${d.value.toLocaleString()}회`)
            })
            .on('mousemove', function (event) {
                tooltip
                    .style('top', (event.pageY - 10) + 'px')
                    .style('left', (event.pageX + 10) + 'px')
            })
            .on('mouseout', function () {
                d3.select(this)
                    .transition()
                    .duration(150)
                    .attr('opacity', 1)

                tooltip.style('visibility', 'hidden')
            })

        // Draw labels (left side)
        svg.append('g')
            .selectAll('text')
            .data(sortedData)
            .join('text')
            .attr('x', margin.left - 8)
            .attr('y', d => (yScale(d.text) || 0) + yScale.bandwidth() / 2)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'end')
            .style('font-size', '12px')
            .style('fill', isDark ? '#a3a3a3' : '#4b5563')
            .text(d => {
                const maxLen = 12
                return d.text.length > maxLen ? d.text.slice(0, maxLen) + '…' : d.text
            })
            .style('opacity', 0)
            .transition()
            .delay(300)
            .duration(300)
            .style('opacity', 1)

        // Draw value labels (right side)
        g.selectAll('.value-label')
            .data(sortedData)
            .join('text')
            .attr('class', 'value-label')
            .attr('x', d => xScale(d.value) + 8)
            .attr('y', d => (yScale(d.text) || 0) + yScale.bandwidth() / 2)
            .attr('dy', '0.35em')
            .style('font-size', '11px')
            .style('font-weight', '500')
            .style('fill', isDark ? '#737373' : '#6b7280')
            .text(d => d.value.toLocaleString())
            .style('opacity', 0)
            .transition()
            .delay(600)
            .duration(300)
            .style('opacity', 1)

        // Cleanup
        return () => {
            tooltip.remove()
        }
    }, [keywords, maxItems, isDark])

    if (!keywords || keywords.length === 0) {
        return (
            <div className="sentiment-bar-chart--empty" data-component="sentiment-bar-chart" data-state="empty">
                <p className="text-sm text-gray-400 text-center">키워드 데이터가 없습니다</p>
            </div>
        )
    }

    return (
        <div ref={containerRef} className="sentiment-bar-chart" data-component="sentiment-bar-chart">
            <svg ref={svgRef} />
        </div>
    )
}
