# Scripts — PTT Joke Meme PWA

Quick-start scripts for development.

## Start Backend

```powershell
.\scripts\start_backend.ps1
```

Installs Python dependencies and starts the FastAPI server at `http://127.0.0.1:8000`.

## Start Frontend

```powershell
.\scripts\start_frontend.ps1
```

Installs npm dependencies and starts the Vite dev server at `http://127.0.0.1:5173`.

## Run Crawler

```powershell
.\scripts\run_crawler.ps1
.\scripts\run_crawler.ps1 -pages 2
.\scripts\run_crawler.ps1 -pages 3
```

Default: 1 page. Max: 3 pages. Each request is delayed 2 seconds.
