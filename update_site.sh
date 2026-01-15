#!/bin/bash
# 데이터 업데이트 및 GitHub Pages 자동 배포 스크립트

set -e  # 에러 발생 시 종료

echo "======================================"
echo "📦 데이터 업데이트 및 배포 시작"
echo "======================================"
echo ""

# 1. 백엔드로 이동하여 데이터 Export
echo "1️⃣  데이터 Export 중..."
cd backend
python3 export_data.py
cd ..
echo ""

# 2. Git 커밋 및 푸시
echo "2️⃣  Git 커밋 및 푸시 중..."
git add frontend/public/data/
git commit -m "chore: 데이터 업데이트 $(date +%Y-%m-%d)" || echo "변경사항 없음"
git push origin main
echo ""

echo "======================================"
echo "✅ 완료! GitHub Actions가 자동으로 배포합니다."
echo "======================================"
echo ""
echo "배포 진행 상황: https://github.com/Otoscor/chatbotmonitoring/actions"
