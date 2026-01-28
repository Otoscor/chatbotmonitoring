
import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete
from models.database import get_db_session, Post, ChatServiceCharacter, init_db
from crawler.multi_crawler import crawl_all_targets
from crawler.character_service_crawler import crawl_all_character_services
from export_data import main as export_main

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def save_posts_to_db(posts):
    """Save crawled posts to the database."""
    if not posts:
        return

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

async def save_characters_to_db(results):
    """Save crawled characters to the database."""
    if not results:
        return

    async with get_db_session() as session:
        total_saved = 0
        
        # Optional: Clear old ranking data or keep history?
        # Model has 'crawled_at', usually rankings are snapshot.
        # But we might want to keep history.
        # For now, just insert new records.
        
        for service, chars in results.items():
            for char_data in chars:
                try:
                    # We can insert a new record for every crawl to track ranking history
                    # Or update if same service/id/date?
                    # Let's simple insert.
                    
                    char_entry = ChatServiceCharacter(
                        service=service,
                        character_id=char_data.character_id,
                        rank=char_data.rank,
                        name=char_data.name,
                        author=char_data.author,
                        views=char_data.views,
                        tags=char_data.tags,
                        description=char_data.description,
                        thumbnail_url=char_data.thumbnail_url,
                        character_url=char_data.character_url,
                        crawled_at=datetime.utcnow()
                    )
                    session.add(char_entry)
                    total_saved += 1
                    
                except Exception as e:
                    logger.error(f"Error saving character {service}/{char_data.name}: {e}")
        
        await session.commit()
        logger.info(f"Saved {total_saved} character rankings to database.")

async def main():
    print("🚀 Starting manual crawl and export...")
    
    # Initialize DB (if needed)
    await init_db()

    # 1. Crawl Communities
    print("\n🕷️  Crawling communities (DCInside, etc)...")
    # Crawling 2 pages for quickness
    posts = await crawl_all_targets(pages=2)
    print(f"✅ Crawled {len(posts)} posts.")

    # 2. Save Posts to DB
    print("\n💾 Saving posts to database...")
    await save_posts_to_db(posts)

    # 3. Crawl Character Services
    print("\n🤖 Crawling character services (Elyn, Caveduck, etc)...")
    # Crawl all services including new ones
    char_results = await crawl_all_character_services()
    count = sum(len(chars) for chars in char_results.values())
    print(f"✅ Crawled {count} characters from {len(char_results)} services.")

    # 4. Save Characters to DB
    print("\n💾 Saving characters to database...")
    await save_characters_to_db(char_results)

    # 5. Export
    print("\n📦 Exporting data...")
    try:
        await export_main()
    except Exception as e:
        logger.error(f"Export failed: {e}")

    print("\n✨ Done!")

if __name__ == "__main__":
    asyncio.run(main())
