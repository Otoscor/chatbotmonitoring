Start servers, run crawling, export data, then commit and push all changes.

This command performs the complete workflow for updating and deploying the monitoring dashboard.

Follow these steps:

## 1. Start servers

Run `npm run start` in background to start both frontend (port 3000) and backend (port 8001)
- Check server startup output after 3 seconds to verify both servers are running
- Frontend should be at http://localhost:3000/
- Backend should be at http://0.0.0.0:8001
- If servers are already running (check with `lsof -ti:3000,8001`), skip this step

## 2. Run crawling (posts)

Execute the posts crawling process via API (this saves to DB automatically):
```bash
curl -X POST "http://localhost:8001/api/crawl" -H "Content-Type: application/json" -d '{"pages": 2}'
```
This collects posts from DCInside and Arcalive communities and saves them to the database.

Target galleries: wrtnai, aichatting, babechat, characterai

## 3. Run crawling (characters)

Execute the character ranking crawling process:
```bash
cd /Users/anipen/Desktop/monitoring/backend
source venv/bin/activate
python -c "import asyncio; from crawler.character_service_crawler import crawl_all_character_services; asyncio.run(crawl_all_character_services())"
```
This collects character rankings from: Zeta, LunaTalk, BabeChat, Crack, Elyn, Caveduck

After crawling, save to database:
```bash
python -c "
import asyncio
from crawler.character_service_crawler import crawl_all_character_services
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models.database import ChatServiceCharacter

async def crawl_and_save():
    results = await crawl_all_character_services()

    engine = create_async_engine('sqlite+aiosqlite:///monitoring.db')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Clear old data
        await session.execute('DELETE FROM chat_service_characters')

        # Insert new data
        for service, characters in results.items():
            for idx, char in enumerate(characters):
                db_char = ChatServiceCharacter(
                    service=service,
                    character_id=char.character_id,
                    rank=idx + 1,
                    name=char.name,
                    author=char.author or 'Unknown',
                    views=char.views or 0,
                    tags=char.tags or [],
                    description=char.description or '',
                    thumbnail_url=char.thumbnail_url or '',
                    character_url=char.character_url or ''
                )
                session.add(db_char)

        await session.commit()

    print(f'Saved {sum(len(v) for v in results.values())} characters')

asyncio.run(crawl_and_save())
"
```

## 4. Run crawling (app reviews)

Execute the app review crawling process:
```bash
cd /Users/anipen/Desktop/monitoring/backend
source venv/bin/activate
python -m crawler.app_review_crawler
```
This collects app reviews from Google Play Store and App Store for 9 apps.

## 5. Export data to JSON

Export database data to static JSON files for Vercel deployment:
```bash
cd /Users/anipen/Desktop/monitoring/backend
source venv/bin/activate
python export_data.py
```
This creates JSON files in `frontend/public/data/` directory.

## 6. Commit changes

- Check git status to see all changes
- Stage the database file: `git add backend/monitoring.db`
- Stage JSON data files: `git add frontend/public/data/`
- Stage any other modified files if needed
- Create a commit with an appropriate message that:
  - Follows the repository's commit style (chore/feat/fix/refactor)
  - Describes what changed (e.g., "chore: 데이터베이스 업데이트")
  - Ends with: Co-Authored-By: Claude <model> <noreply@anthropic.com>
- IMPORTANT: Always include backend/monitoring.db AND frontend/public/data/ in the commit

## 7. Push to remote

Run `git push origin main`
- This triggers automatic Vercel deployment
- Vercel will rebuild and deploy the updated frontend with new JSON data

## 8. Show final status

Display the final git status and summary:
- Number of posts crawled
- Number of characters crawled
- Number of app reviews crawled
- Files committed
- Vercel deployment status (auto-triggered by push)

---

Use heredoc format for commit messages:
```bash
git commit -m "$(cat <<'EOF'
Commit message here

Co-Authored-By: Claude <model> <noreply@anthropic.com>
EOF
)"
```

Never commit sensitive files like .env or credentials.
