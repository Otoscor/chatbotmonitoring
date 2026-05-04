/**
 * 리뷰 카드 컴포넌트
 */
import { type AppReview } from '../../../utils/api'

interface ReviewCardProps {
  review: AppReview
}

const getRatingStars = (rating: number) => '★'.repeat(rating) + '☆'.repeat(5 - rating)

const getRatingColor = (rating: number) => {
  if (rating >= 4) return 'text-gray-700'
  if (rating >= 3) return 'text-gray-600'
  return 'text-gray-400'
}

export function ReviewCard({ review }: ReviewCardProps) {
  return (
    <article className="review-card" data-review-id={review.id}>
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className={`review-rating ${getRatingColor(review.rating)}`}>
            {getRatingStars(review.rating)}
          </div>
          <div className="review-meta">
            {review.reviewer_name || '익명'} · {review.platform === 'google_play' ? '구글 플레이' : '앱스토어'}
            {review.review_date && ` · ${new Date(review.review_date).toLocaleDateString()}`}
          </div>
        </div>
      </div>
      {review.review_text && <p className="review-text">{review.review_text}</p>}
    </article>
  )
}
