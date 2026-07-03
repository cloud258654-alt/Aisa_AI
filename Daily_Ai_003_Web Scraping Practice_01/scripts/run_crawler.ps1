# Run Crawler — PTT Joke Meme PWA
param(
    [int]$pages = 1
)

if ($pages -gt 3) {
    Write-Host "ERROR: Maximum pages allowed is 3, got $pages" -ForegroundColor Red
    exit 1
}

Write-Host "=== Running PTT Joke Crawler ===" -ForegroundColor Cyan
Write-Host "Pages: $pages" -ForegroundColor Yellow
Write-Host "Delay: 2s" -ForegroundColor Yellow

python ../backend/run_crawler.py --pages $pages

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== Crawler completed ===" -ForegroundColor Green
} else {
    Write-Host "=== Crawler failed ===" -ForegroundColor Red
}
