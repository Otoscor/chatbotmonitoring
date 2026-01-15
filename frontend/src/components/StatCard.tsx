import { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: number | string
  description?: string
}

export default function StatCard({ title, value, description }: StatCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded p-4 hover:border-gray-300 transition-colors">
      <div className="text-xs text-gray-500 mb-1">{title}</div>
      <div className="text-2xl font-semibold text-gray-900 mb-0.5">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {description && (
        <div className="text-xs text-gray-400 mt-1">{description}</div>
      )}
    </div>
  )
}
