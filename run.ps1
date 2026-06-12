# Flask 서버 실행 스크립트

# 가상환경 활성화
Write-Host "🔧 가상환경 활성화 중..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "🚀 네이버 메일 AI 자동화 요약 서버 시작" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📍 접속 주소: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🛑 종료: Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚙️  Flask 설정:" -ForegroundColor Cyan
Write-Host "   - 호스트: localhost" -ForegroundColor Gray
Write-Host "   - 포트: 5000" -ForegroundColor Gray
Write-Host "   - 디버그 모드: ON" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 기능:" -ForegroundColor Cyan
Write-Host "   - API 키 없으면 모의 데이터 제공" -ForegroundColor Gray
Write-Host "   - Chrome 원격 디버깅으로 실제 메일 수집 가능" -ForegroundColor Gray
Write-Host "   - Google Gemini로 AI 분석" -ForegroundColor Gray
Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Flask 서버 시작
python app.py
