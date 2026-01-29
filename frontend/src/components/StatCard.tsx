interface StatCardProps {
  title: string
  value: number | string
  description?: string
}

export default function StatCard({ title, value, description }: StatCardProps) {
  return (
    <div className="stat-card" data-component="stat-card">
      <div className="stat-card-title">{title}</div>
      <div className="stat-card-value">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {description && (
        <div className="stat-card-description">{description}</div>
      )}
    </div>
  )
}
