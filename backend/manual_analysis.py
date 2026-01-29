
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from models.database import AsyncSessionLocal, Post, PostKeyword, CharacterMention

# 분석기 임포트
from analyzer.keyword_extractor import extract_keywords_tfidf
from analyzer.character_ranker import rank_characters

async def run_manual_analysis():
    print("🔄 수동 데이터 분석 시작...")
    
    async with AsyncSessionLocal() as session:
        # 1. 최근 7일 게시글 조회
        days_ago = datetime.utcnow() - timedelta(days=7)
        query = select(Post).where(Post.created_at >= days_ago)
        result = await session.execute(query)
        posts = result.scalars().all()
        
        print(f"  - 최근 7일 게시글: {len(posts)}개 조회됨")
        
        if not posts:
            print("  - 분석할 데이터가 없습니다.")
            return

        # 2. 키워드 추출 및 저장
        print("  - 키워드 추출 중...")
        titles = [p.title for p in posts if p.title]
        keywords = extract_keywords_tfidf(titles, top_n=50)
        
        # 기존 키워드 삭제 (중복 방지)
        # 실제로는 post_id 별로 해야 하지만, 여기서는 간단히 트렌드용 집계만 필요하므로
        # PostKeyword 테이블에 대량으로 넣거나, DailyReport 업데이트 방식 고려.
        # 하지만 export_data.py는 PostKeyword 테이블을 참조하므로, 여기에 데이터를 넣어야 함.
        
        # 주의: PostKeyword는 Post와 1:N 관계임.
        # 간단히 하기 위해: 각 게시글별로 키워드를 추출해서 넣어야 정석이지만,
        # 여기서는 "전체 트렌드"를 위해 가상의 인기 키워드를 일부 게시글에 매핑하거나
        # 또는 전체 타이틀 뭉치에서 상위 키워드를 뽑아서, 해당 키워드가 포함된 게시글에 태깅하는 방식 사용.
        
        # 더 정확한 방법: 각 게시글마다 키워드 추출
        # (시간이 걸릴 수 있음)
        
        # 여기서는 "빠른 업데이트"를 위해 상위 키워드만 추출하여
        # 해당 키워드를 포함하는 게시글을 찾아 PostKeyword에 등록
        
        for kw in keywords:
            keyword_text = kw['keyword']
            score = kw.get('score', 1.0)
            
            # 이 키워드를 포함하는 게시글 찾기 (LIKE 검색)
            target_posts = [p for p in posts if keyword_text in p.title]
            
            for post in target_posts:
                # 이미 존재하는지 확인
                existing_q = select(PostKeyword).where(
                    PostKeyword.post_id == post.id,
                    PostKeyword.keyword == keyword_text
                )
                existing = await session.execute(existing_q)
                if not existing.scalar():
                    new_kw = PostKeyword(
                        post_id=post.id,
                        keyword=keyword_text,
                        score=score
                    )
                    session.add(new_kw)
        
        print("  ✓ 키워드 데이터 업데이트 완료")
        
        # 3. 캐릭터 언급 분석 및 저장
        print("  - 캐릭터 랭킹 분석 중...")
        character_rankings = rank_characters(titles, top_n=30)
        
        # CharacterMention 테이블 업데이트
        # mention_date는 오늘 날짜로 통일 (또는 게시글 날짜따라 가야하지만 복잡함)
        today = datetime.utcnow()
        
        for char in character_rankings:
            name = char['name']
            count = char['mentions']
            
            # 오늘자 해당 캐릭터 언급 있는지 확인
            existing_q = select(CharacterMention).where(
                CharacterMention.character_name == name,
                CharacterMention.mention_date >= today.date() # 오늘 날짜 기준
            )
            # 여기선 단순히 추가 (중복 합산은 export 시 처리됨)
            new_mention = CharacterMention(
                character_name=name,
                mention_date=today,
                mention_count=count,
                source_gallery="manual_analysis"
            )
            session.add(new_mention)
            
        print("  ✓ 캐릭터 랭킹 데이터 업데이트 완료")
        
        await session.commit()
        print("✨ 분석 데이터 저장 완료")

if __name__ == "__main__":
    asyncio.run(run_manual_analysis())
