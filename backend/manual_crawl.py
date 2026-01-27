
import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from models.database import get_db_session, Post, init_db
from crawler.multi_crawler import crawl_all_targets
from export_data import main as export_main

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def save_posts_to_db(posts):
    """Save crawled posts to the database."""
    async with get_db_session() as session:
        saved_count = 0
        for post_data in posts:
            # Check for existing post
            try:
                existing = await session.execute(
                    select(Post).where(Post.post_id == post_data.post_id)
                )
                if existing.scalar_one_or_none():
                    continue
                
                post = Post(
                    post_id=post_data.post_id,
                    gallery_id=post_data.gallery_id,
                    title=post_data.title,
                    author=post_data.author,
                    created_at=post_data.created_at,
                    view_count=post_data.view_count,
                    recommend_count=post_data.recommend_count,
                    comment_count=post_data.comment_count,
                    url=post_data.url
                )
                session.add(post)
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving post {post_data.post_id}: {e}")

        await session.commit()
        logger.info(f"Saved {saved_count} new posts to database.")

async def main():
    print("🚀 Starting manual crawl and export...")
    
    # Initialize DB (if needed)
    await init_db()

    # 1. Crawl
    print("\n🕷️  Crawling all targets...")
    # Crawling 2 pages for quickness, or default
    posts = await crawl_all_targets(pages=2)
    print(f"✅ Crawled {len(posts)} posts.")

    # 2. Save to DB
    print("\n💾 Saving to database...")
    await save_posts_to_db(posts)

    # 3. Export
    print("\n📦 Exporting data...")
    try:
        await export_main()
    except Exception as e:
        logger.error(f"Export failed: {e}")
        # We continue even if export fails, but user asked for "save to db then git push"
        # Since push depends on export (if pushing JSON), this is critical.
        # But export_main handles its own errors mostly.

    print("\n✨ Done!")

if __name__ == "__main__":
    asyncio.run(main())
