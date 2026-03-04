Start servers, run crawling, then commit and push all changes.

Follow these steps:

1. **Start servers**: Run `npm run start` in background to start both frontend (port 3000) and backend (port 8001)
   - Check server startup output after 3 seconds to verify both servers are running
   - Frontend should be at http://localhost:3000/
   - Backend should be at http://0.0.0.0:8001

2. **Run crawling**: Execute the crawling process
   - Check if there's a crawl skill or script available
   - If available, use `/crawl` or appropriate crawling command
   - Wait for crawling to complete before proceeding

3. **Commit changes**:
   - Check git status to see all changes
   - Run git diff to review the changes (especially monitoring.db)
   - Check recent commit messages with git log to match the commit style
   - Stage modified files (prefer specific files over "git add .")
   - Create a commit with an appropriate message that:
     - Follows the repository's commit style (chore/feat/fix/refactor)
     - Describes what changed (e.g., "chore: 데이터베이스 업데이트")
     - Ends with: Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

4. **Push to remote**: Run `git push origin main`

5. **Show final status**: Display the final git status

Use heredoc format for commit messages:
```bash
git commit -m "$(cat <<'EOF'
Commit message here

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

Never commit sensitive files like .env or credentials.
