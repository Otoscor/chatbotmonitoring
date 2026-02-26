import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useSpring, animated, config } from '@react-spring/web'
import { useGesture } from '@use-gesture/react'
import { useTheme } from '../hooks/useTheme'

interface BubbleItem {
    text: string
    value: number
    sentiment?: number
}

interface BubbleChartProps {
    keywords: BubbleItem[]
}

export default function BubbleChart({ keywords }: BubbleChartProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const svgRef = useRef<SVGSVGElement>(null)
    const gRef = useRef<SVGGElement>(null)
    const [dimensions, setDimensions] = useState({ width: 600, height: 300 })
    const scaleRef = useRef(1) // Track scale in ref for wheel handler
    const { isDark } = useTheme()

    // Spring state for transform (x, y, scale)
    const [{ x, y, scale }, api] = useSpring(() => ({
        x: 0,
        y: 0,
        scale: 1,
        config: { ...config.gentle, friction: 40 } // Higher friction for smoother inertia decay
    }))

    // Update dimensions on mount and resize
    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                const { width } = containerRef.current.getBoundingClientRect()
                // Responsive height: smaller on mobile
                const isMobile = window.innerWidth <= 768
                const height = isMobile ? 220 : 300
                setDimensions({ width, height })
                // Center the initial position
                api.start({ x: width / 2, y: height / 2 })
            }
        }

        updateDimensions()
        window.addEventListener('resize', updateDimensions)
        return () => window.removeEventListener('resize', updateDimensions)
    }, [api])

    // Drag gesture binding (using bind() approach)
    const bind = useGesture(
        {
            onDrag: ({ offset: [ox, oy] }) => {
                api.start({
                    x: ox,
                    y: oy,
                    config: config.gentle
                })
            }
        },
        {
            drag: {
                from: () => [x.get(), y.get()],
                rubberband: 0.15
            }
        }
    )

    // Wheel zoom with native event listener for proper passive:false
    useEffect(() => {
        const container = containerRef.current
        if (!container) return

        const handleWheel = (e: WheelEvent) => {
            e.preventDefault()
            const dampening = 0.0008
            const currentScale = scaleRef.current
            const newScale = Math.max(0.5, Math.min(5, currentScale - e.deltaY * dampening))
            scaleRef.current = newScale
            // Use set() for instant response without animation overhead
            api.set({ scale: newScale })
        }

        container.addEventListener('wheel', handleWheel, { passive: false })
        return () => container.removeEventListener('wheel', handleWheel)
    }, [api]) // Remove scale from deps since we use ref

    // D3 rendering effect
    useEffect(() => {
        if (!keywords || keywords.length === 0 || !svgRef.current || !gRef.current) return

        const g = d3.select(gRef.current)

        // Clear previous content
        g.selectAll('*').remove()

        // Prepare data
        const maxValue = d3.max(keywords, d => d.value) || 1
        const radiusScale = d3.scaleSqrt<number>()
            .domain([0, maxValue])
            .range([20, 55])

        const nodes = keywords.map(d => ({
            ...d,
            r: radiusScale(d.value),
            x: 0,
            y: 0
        }))

        // Sentiment Opacity Scale
        const opacityScale = d3.scaleLinear<number>()
            .domain([0, 1])
            .range([0.1, 0.5])
            .clamp(true)

        // Force Simulation
        const simulation = d3.forceSimulation(nodes as any)
            .force('charge', d3.forceManyBody().strength(5))
            .force('collide', d3.forceCollide().radius((d: any) => d.r + 8).iterations(2))
            .force('x', d3.forceX(0).strength(0.05))
            .force('y', d3.forceY(0).strength(0.15))

        // Run initial layout synchronously then stop
        for (let i = 0; i < 300; ++i) simulation.tick()
        simulation.stop() // Stop simulation to prevent continuous updates

        // Color helpers
        const getFillColor = (d: any) => {
            const sentiment = d.sentiment
            if (typeof sentiment === 'undefined') {
                if (isDark) {
                    const scale = d3.scaleLinear<string>().domain([0, maxValue]).range(['#404040', '#a3a3a3'])
                    return scale(d.value)
                } else {
                    const scale = d3.scaleLinear<string>().domain([0, maxValue]).range(['#d4d4d4', '#525252'])
                    return scale(d.value)
                }
            }
            if (sentiment >= 0.3) return '#ACFFC4'
            if (sentiment <= -0.3) return '#FFACAC'
            return isDark ? '#525252' : '#9ca3af'
        }

        const getOpacity = (d: any) => {
            const sentiment = d.sentiment
            if (typeof sentiment === 'undefined') return 1
            if (Math.abs(sentiment) >= 0.3) {
                return opacityScale(Math.abs(sentiment))
            }
            return 1
        }

        // Create tooltip
        const tooltip = d3.select('body').append('div')
            .attr('class', 'bubble-tooltip')
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

        // Render nodes
        const bubbleGroup = g.selectAll('g.bubble')
            .data(nodes)
            .join('g')
            .attr('class', 'bubble')
            .attr('transform', (d: any) => `translate(${d.x},${d.y})`)

        // Circles
        bubbleGroup.append('circle')
            .attr('r', 0)
            .attr('fill', (d: any) => getFillColor(d))
            .attr('fill-opacity', (d: any) => getOpacity(d))
            .attr('stroke', (d: any) => getFillColor(d))
            .attr('stroke-width', 1.5)
            .attr('stroke-opacity', (d: any) => getOpacity(d))
            .style('cursor', 'pointer')
            .transition()
            .duration(800)
            .delay((_, i) => i * 30)
            .ease(d3.easeElasticOut.amplitude(1).period(0.5))
            .attr('r', (d: any) => d.r)

        // Text
        bubbleGroup.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .style('font-size', (d: any) => `${Math.min(d.r / 2.5, 14)}px`)
            .style('fill', (d: any) => {
                const sentiment = d.sentiment
                if (typeof sentiment !== 'undefined' && Math.abs(sentiment) >= 0.3) {
                    return '#1f2937'
                }
                if (isDark) return '#ffffff'
                const maxVal = d3.max(keywords, k => k.value) || 1
                return d.value > maxVal * 0.5 ? '#ffffff' : '#1f2937'
            })
            .style('pointer-events', 'none')
            .style('font-weight', '500')
            .text((d: any) => {
                const text = d.text
                const maxLength = Math.floor(d.r / 3.5)
                return text.length > maxLength ? text.slice(0, maxLength) + '…' : text
            })
            .style('opacity', 0)
            .transition()
            .delay(800)
            .duration(300)
            .style('opacity', 1)

        // Interactivity
        bubbleGroup.selectAll('circle')
            .on('mouseover', function (_event, d: any) {
                const currentOpacity = getOpacity(d)
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('stroke-width', 3)
                    .attr('fill-opacity', Math.min(currentOpacity + 0.2, 1))
                    .attr('stroke-opacity', 1)

                const sentimentLabel = d.sentiment >= 0.3 ? '긍정' :
                    d.sentiment <= -0.3 ? '부정' : '중립'

                let tooltipContent = `<strong>${d.text}</strong><br/>언급 횟수: ${d.value.toLocaleString()}회`
                if (typeof d.sentiment !== 'undefined') {
                    tooltipContent += `<br/>감정: ${sentimentLabel} (${d.sentiment})`
                }

                tooltip
                    .style('visibility', 'visible')
                    .html(tooltipContent)
            })
            .on('mousemove', function (event) {
                tooltip
                    .style('top', (event.pageY - 10) + 'px')
                    .style('left', (event.pageX + 10) + 'px')
            })
            .on('mouseout', function (_event, d: any) {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('stroke-width', 1.5)
                    .attr('fill-opacity', getOpacity(d))
                    .attr('stroke-opacity', getOpacity(d))

                tooltip.style('visibility', 'hidden')
            })

        // Update positions on simulation tick
        simulation.on('tick', () => {
            bubbleGroup.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
        })

        return () => {
            simulation.stop()
            tooltip.remove()
        }
    }, [keywords, isDark])

    if (!keywords || keywords.length === 0) {
        return (
            <div className="bubble-chart--empty" data-component="bubble-chart" data-state="empty">
                <p className="text-sm text-gray-400 text-center">해시태그 데이터가 없습니다</p>
            </div>
        )
    }

    return (
        <div
            ref={containerRef}
            className="bubble-chart relative touch-none select-none"
            data-component="bubble-chart"
            {...bind()}
            style={{ cursor: 'grab' }}
        >
            <svg ref={svgRef} width={dimensions.width} height={dimensions.height}>
                <animated.g
                    ref={gRef}
                    style={{
                        transform: x.to((xVal) =>
                            `translate(${xVal}px, ${y.get()}px) scale(${scale.get()})`
                        )
                    }}
                />
            </svg>
        </div>
    )
}
