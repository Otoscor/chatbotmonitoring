"""
최신 DailyReport의 top_keywords를 현재 필터 기준으로 재생성
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, desc
from models.database import AsyncSessionLocal, Post, DailyReport, init_db
from analyzer.keyword_extractor import extract_keywords_tfidf


async def regen():
    await init_db()

    async with AsyncSessionLocal() as session:
        # 최신 리포트 조회
        report_q = select(DailyReport).order_by(desc(DailyReport.report_date)).limit(1)
        result = await session.execute(report_q)
        report = result.scalar_one_or_none()

        if not report:
            print("❌ DailyReport가 없습니다.")
            return

        print(f"📄 리포트 날짜: {report.report_date}")

        # 최근 7일 게시글 조회
        since = datetime.utcnow() - timedelta(days=7)
        posts_q = select(Post).where(Post.created_at >= since)
        posts_result = await session.execute(posts_q)
        posts = posts_result.scalars().all()

        print(f"📝 분석 대상 게시글: {len(posts)}개")

        titles = [p.title for p in posts if p.title]
        if not titles:
            print("❌ 분석할 제목이 없습니다.")
            return

        # 새 필터 기준으로 키워드 재추출
        new_keywords = extract_keywords_tfidf(titles, top_n=50)
        print(f"🔑 추출된 키워드 수: {len(new_keywords)}개")
        print(f"   Top 10: {[k['keyword'] for k in new_keywords[:10]]}")

        # DB 업데이트
        report.top_keywords = new_keywords
        await session.commit()
        print("✅ top_keywords 업데이트 완료")


if __name__ == "__main__":
    asyncio.run(regen())
