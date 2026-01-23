
interface NewChatService {
    id: number
    service_name: string
    service_name_en: string
    service_type: 'web' | 'app' | 'both'
    description: string | null
    launch_date: string | null
    web_url: string | null
    ios_url: string | null
    android_url: string | null
    logo_url: string | null
    features: string[]
    status: 'active' | 'beta' | 'closed'
}

interface ServiceCardProps {
    service: NewChatService
}

export default function ServiceCard({ service }: ServiceCardProps) {
    const formatDate = (dateString: string | null) => {
        if (!dateString) return '출시 예정'
        const date = new Date(dateString)
        return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })
    }

    const handleCardClick = () => {
        // 웹 서비스가 있으면 웹으로, 없으면 앱스토어 (iOS 우선)
        let targetUrl = null

        if (service.web_url) {
            targetUrl = service.web_url
        } else if (service.ios_url) {
            targetUrl = service.ios_url
        } else if (service.android_url) {
            targetUrl = service.android_url
        }

        if (targetUrl) {
            window.open(targetUrl, '_blank', 'noopener,noreferrer')
        }
    }

    const getServiceTypeLabel = () => {
        if (service.service_type === 'web') return 'Web'
        if (service.service_type === 'app') return 'App'
        return 'Web · App'
    }

    const isClickable = service.web_url || service.ios_url || service.android_url

    return (
        <div
            onClick={isClickable ? handleCardClick : undefined}
            className={`block bg-white border border-gray-200 rounded p-4 transition-all overflow-hidden ${isClickable ? 'cursor-pointer hover:border-gray-300 hover:shadow-sm' : ''
                }`}
        >
            {/* 헤더 */}
            <div className="flex items-start justify-between mb-3">
                <div>
                    <h3 className="text-sm font-medium text-gray-900">{service.service_name}</h3>
                    <p className="text-xs text-gray-500 mt-0.5">{service.service_name_en}</p>
                </div>
                <span className="text-xs text-gray-400">{getServiceTypeLabel()}</span>
            </div>

            {/* 설명 */}
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {service.description || '설명이 없습니다.'}
            </p>

            {/* 주요 기능 */}
            {service.features && service.features.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                    {service.features.slice(0, 3).map((feature, idx) => (
                        <span
                            key={idx}
                            className="inline-block px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                        >
                            {feature}
                        </span>
                    ))}
                    {service.features.length > 3 && (
                        <span className="inline-block px-1.5 py-0.5 text-xs text-gray-400">
                            +{service.features.length - 3}
                        </span>
                    )}
                </div>
            )}

            {/* 하단 정보 */}
            <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{formatDate(service.launch_date)}</span>
                {service.status === 'beta' && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded">베타</span>
                )}
            </div>
        </div>
    )
}
