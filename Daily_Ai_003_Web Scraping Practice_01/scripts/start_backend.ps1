# Start Backend — PTT Joke Meme PWA
Write-Host "=== Installing dependencies ===" -ForegroundColor Cyan
pip install -r ../backend/requirements.txt

Write-Host "=== Starting FastAPI backend ===" -ForegroundColor Cyan
Write-Host "Server: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
