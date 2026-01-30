import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useSpring, animated, config } from '@react-spring/web'
import { useGesture } from '@use-gesture/react'

interface NetworkNode {
    id: string
    text: string
    value: number
    x?: number
    y?: number
    fx?: number | null
    fy?: number | null
}

interface NetworkLink {
    source: string | NetworkNode
    target: string | NetworkNode
    value: number
}

interface NetworkGraphProps {
    keywords: { text: string; value: number }[]
}

export default function NetworkGraph({ keywords }: NetworkGraphProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const svgRef = useRef<SVGSVGElement>(null)
    const gRef = useRef<SVGGElement>(null)
    const [dimensions, setDimensions] = useState({ width: 600, height: 320 })
    const scaleRef = useRef(2) // Track scale in ref for wheel handler (initial scale = 2)

    // Spring state for transform (x, y, scale)
    const [{ x, y, scale }, api] = useSpring(() => ({
        x: 0,
        y: 0,
        scale: 2, // Initial scale matching previous implementation
        config: { ...config.gentle, friction: 40 }
    }))

    // Update dimensions on mount and resize
    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                const { width } = containerRef.current.getBoundingClientRect()
                // Responsive height: smaller on mobile
                const isMobile = window.innerWidth <= 768
                const height = isMobile ? 250 : 320
                setDimensions({ width, height })
                // Center the initial position with zoom 2
                api.start({ x: -width / 2, y: -height / 2, scale: 2 })
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
                // Keep refs in sync with drag position
                xRef.current = ox
                yRef.current = oy
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

    // Track position in refs for wheel handler
    const xRef = useRef(-300) // Will be updated on mount
    const yRef = useRef(-160)

    // Sync refs with spring on mount
    useEffect(() => {
        if (containerRef.current) {
            const { width } = containerRef.current.getBoundingClientRect()
            xRef.current = -width / 2
            yRef.current = -160
        }
    }, [])

    // Wheel zoom with mouse-centered calculation
    useEffect(() => {
        const container = containerRef.current
        if (!container) return

        const handleWheel = (e: WheelEvent) => {
            e.preventDefault()

            const rect = container.getBoundingClientRect()
            // Mouse position relative to container
            const mouseX = e.clientX - rect.left
            const mouseY = e.clientY - rect.top

            const oldScale = scaleRef.current
            const dampening = 0.001
            const newScale = Math.max(0.3, Math.min(5, oldScale - e.deltaY * dampening))

            if (oldScale === newScale) return

            // Calculate new translate to keep mouse point fixed
            // Formula: newTranslate = mousePos - (mousePos - oldTranslate) * (newScale / oldScale)
            const scaleRatio = newScale / oldScale
            const newX = mouseX - (mouseX - xRef.current) * scaleRatio
            const newY = mouseY - (mouseY - yRef.current) * scaleRatio

            // Update refs
            scaleRef.current = newScale
            xRef.current = newX
            yRef.current = newY

            // Apply immediately
            api.set({ scale: newScale, x: newX, y: newY })
        }

        container.addEventListener('wheel', handleWheel, { passive: false })
        return () => container.removeEventListener('wheel', handleWheel)
    }, [api]) // Remove scale from deps since we use ref

    useEffect(() => {
        if (!keywords || keywords.length === 0 || !svgRef.current || !gRef.current || !containerRef.current) return

        const { width } = containerRef.current.getBoundingClientRect()
        const height = 320
        const svg = d3.select(svgRef.current)
        const contentGroup = d3.select(gRef.current)

        // Clear previous content
        contentGroup.selectAll('*').remove()

        // Check dark mode
        const isDarkMode = document.documentElement.classList.contains('dark') ||
            window.matchMedia('(prefers-color-scheme: dark)').matches

        // Prepare nodes from keywords
        const nodes: NetworkNode[] = keywords.map(k => ({
            id: k.text,
            text: k.text,
            value: k.value
        }))

        // Create links
        const links: NetworkLink[] = []
        const sortedNodes = [...nodes].sort((a, b) => b.value - a.value)

        // Connect nodes
        for (let i = 0; i < sortedNodes.length; i++) {
            const connectCount = Math.min(2, sortedNodes.length - i - 1)
            for (let j = 1; j <= connectCount; j++) {
                if (i + j < sortedNodes.length) {
                    links.push({
                        source: sortedNodes[i].id,
                        target: sortedNodes[i + j].id,
                        value: (sortedNodes[i].value + sortedNodes[i + j].value) / 2
                    })
                }
            }
            if (sortedNodes.length > 4 && i < sortedNodes.length - 3) {
                const randomOffset = 3 + Math.floor(Math.random() * Math.min(3, sortedNodes.length - i - 3))
                if (i + randomOffset < sortedNodes.length) {
                    links.push({
                        source: sortedNodes[i].id,
                        target: sortedNodes[i + randomOffset].id,
                        value: (sortedNodes[i].value + sortedNodes[i + randomOffset].value) / 4
                    })
                }
            }
        }

        // Size & Color scales
        const maxValue = d3.max(nodes, d => d.value) || 1
        const sizeScale = d3.scaleLinear()
            .domain([0, maxValue])
            .range([8, 28])

        const colorScale = d3.scaleLinear<string>()
            .domain([0, maxValue])
            .range(isDarkMode ? ['#404040', '#a3a3a3'] : ['#d4d4d4', '#525252'])

        // Create tooltip
        const tooltip = d3.select('body').append('div')
            .attr('class', 'network-tooltip')
            .style('position', 'absolute')
            .style('visibility', 'hidden')
            .style('background-color', isDarkMode ? '#1a1a1a' : '#ffffff')
            .style('border', `1px solid ${isDarkMode ? '#333' : '#e5e7eb'}`)
            .style('padding', '8px 12px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('color', isDarkMode ? '#ffffff' : '#111827')
            .style('pointer-events', 'none')
            .style('z-index', '9999')
            .style('box-shadow', '0 2px 8px rgba(0,0,0,0.15)')

        // Force Simulation
        const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
            .force('link', d3.forceLink(links)
                .id((d: any) => d.id)
                .distance(80)
                .strength(0.3))
            .force('charge', d3.forceManyBody().strength(-150))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius((d: any) => sizeScale(d.value) + 5))

        // Draw links
        const link = contentGroup.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', isDarkMode ? '#333' : '#e5e7eb')
            .attr('stroke-width', 1)
            .attr('stroke-opacity', 0.6)

        // Draw nodes
        const node = contentGroup.append('g')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .style('cursor', 'grab')
            .call(d3.drag<SVGGElement, NetworkNode>()
                .on('start', (event, d) => {
                    // Prevent gesture panning when dragging nodes
                    event.sourceEvent.stopPropagation()
                    d3.select(event.currentTarget as SVGGElement).style('cursor', 'grabbing')
                    if (!event.active) simulation.alphaTarget(0.3).restart()
                    d.fx = d.x
                    d.fy = d.y
                })
                .on('drag', (event, d) => {
                    d.fx = event.x
                    d.fy = event.y
                })
                .on('end', (event, d) => {
                    d3.select(event.currentTarget as SVGGElement).style('cursor', 'grab')
                    if (!event.active) simulation.alphaTarget(0)
                    d.fx = null
                    d.fy = null
                }) as any)

        // Add circles
        node.append('circle')
            .attr('r', 0)
            .attr('fill', d => colorScale(d.value))
            .attr('stroke', isDarkMode ? '#525252' : '#e5e7eb')
            .attr('stroke-width', 1.5)
            .transition()
            .duration(600)
            .delay((_, i) => i * 30)
            .attr('r', d => sizeScale(d.value))

        // Add labels
        node.append('text')
            .text(d => {
                const maxLen = Math.max(4, Math.floor(sizeScale(d.value) / 3))
                return d.text.length > maxLen ? d.text.slice(0, maxLen) + '…' : d.text
            })
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .style('font-size', d => `${Math.min(sizeScale(d.value) / 2.5, 11)}px`)
            .style('fill', d => {
                const threshold = maxValue * 0.5
                return isDarkMode
                    ? (d.value > threshold ? '#1a1a1a' : '#ffffff')
                    : (d.value > threshold ? '#ffffff' : '#374151')
            })
            .style('pointer-events', 'none')
            .style('font-weight', '500')
            .style('opacity', 0)
            .transition()
            .delay(600)
            .duration(300)
            .style('opacity', 1)

        // Interactivity
        node.on('mouseover', function (_event, d) {
            d3.select(this).select('circle')
                .transition()
                .duration(150)
                .attr('stroke-width', 3)
                .attr('stroke', isDarkMode ? '#a3a3a3' : '#374151')

            link
                .attr('stroke-opacity', l =>
                    (l.source as NetworkNode).id === d.id || (l.target as NetworkNode).id === d.id ? 1 : 0.2)
                .attr('stroke-width', l =>
                    (l.source as NetworkNode).id === d.id || (l.target as NetworkNode).id === d.id ? 2 : 1)

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
                d3.select(this).select('circle')
                    .transition()
                    .duration(150)
                    .attr('stroke-width', 1.5)
                    .attr('stroke', isDarkMode ? '#525252' : '#e5e7eb')

                link
                    .attr('stroke-opacity', 0.6)
                    .attr('stroke-width', 1)

                tooltip.style('visibility', 'hidden')
            })

        // Run simulation synchronously for stable layout
        for (let i = 0; i < 300; ++i) simulation.tick()
        simulation.stop()

        // Apply final positions statically (no continuous tick updates)
        link
            .attr('x1', d => (d.source as NetworkNode).x || 0)
            .attr('y1', d => (d.source as NetworkNode).y || 0)
            .attr('x2', d => (d.target as NetworkNode).x || 0)
            .attr('y2', d => (d.target as NetworkNode).y || 0)

        node.attr('transform', d => `translate(${d.x || 0},${d.y || 0})`)

        // Only update positions during active node drag
        simulation.on('tick', () => {
            link
                .attr('x1', d => (d.source as NetworkNode).x || 0)
                .attr('y1', d => (d.source as NetworkNode).y || 0)
                .attr('x2', d => (d.target as NetworkNode).x || 0)
                .attr('y2', d => (d.target as NetworkNode).y || 0)

            node.attr('transform', d => `translate(${d.x || 0},${d.y || 0})`)
        })

        return () => {
            simulation.stop()
            tooltip.remove()
        }
    }, [keywords])

    if (!keywords || keywords.length === 0) {
        return (
            <div className="network-graph--empty" data-component="network-graph" data-state="empty">
                <p className="text-sm text-gray-400 text-center">해시태그 데이터가 없습니다</p>
            </div>
        )
    }

    return (
        <div
            ref={containerRef}
            className="network-graph relative touch-none select-none"
            data-component="network-graph"
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
