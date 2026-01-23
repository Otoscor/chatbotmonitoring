import { useEffect, useState } from 'react'
import ServiceCard from '../components/ServiceCard'
import { USE_STATIC_DATA, API_URL } from '../utils/api'
import axios from 'axios'

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

export default function NewChatServices() {
    const [services, setServices] = useState<NewChatService[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchServices()
    }, [])

    const fetchServices = async () => {
        try {
            setLoading(true)
            setError(null)

            if (USE_STATIC_DATA) {
                // 정적 데이터 모드
                const response = await fetch('/chatbotmonitoring/data/new_chat_services.json')
                if (!response.ok) throw new Error('데이터를 불러올 수 없습니다')
                const data = await response.json()
                setServices(data)
            } else {
                // API 모드
                const response = await axios.get(`${API_URL}/new-chat-services`)
                setServices(response.data)
            }
        } catch (err: any) {
            console.error('신규 서비스 조회 실패:', err)
            setError(err.message || '데이터를 불러오는 중 오류가 발생했습니다')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <p className="text-sm text-gray-500 mb-4">{error}</p>
                    <button
                        onClick={fetchServices}
                        className="px-4 py-2 bg-gray-900 text-white text-sm rounded hover:bg-gray-800 transition-colors"
                    >
                        다시 시도
                    </button>
                </div>
            </div>
        )
    }

    const activeServices = services.filter(s => s.status === 'active')
    const betaServices = services.filter(s => s.status === 'beta')

    return (
        <div className="space-y-6">
            {/* 헤더 */}
            <div className="pb-6 border-b border-gray-200">
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">신규 캐릭터챗 서비스</h1>
                <p className="text-sm text-gray-500">2025-2026년에 런칭한 한국 캐릭터챗 서비스</p>
            </div>

            {/* 서비스 그리드 */}
            {services.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-sm text-gray-500">등록된 신규 서비스가 없습니다</p>
                </div>
            ) : (
                <div>
                    {/* 통계 */}
                    <div className="flex items-center gap-6 mb-6 text-sm text-gray-500">
                        <span>전체 {services.length}개</span>
                        <span>운영 중 {activeServices.length}개</span>
                        {betaServices.length > 0 && <span>베타 {betaServices.length}개</span>}
                    </div>

                    {/* 카드 그리드 - 4열 레이아웃 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {services.map((service) => (
                            <ServiceCard key={service.id} service={service} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
