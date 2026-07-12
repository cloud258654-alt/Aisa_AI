# BI-RMP 本機 n8n + LINE Workflow 架設

## 0. 架構

LINE 使用者 → LINE Platform → Cloudflare Tunnel HTTPS → n8n `/webhook/line/events` → BI-RMP Backend → LINE Reply API

附件 workflow 依賴以下四個環境變數：

- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `BI_RMP_INTERNAL_API_KEY`
- `BI_RMP_BACKEND_BASE_URL`

後端必須提供：

- `POST /api/line/client-recognition`
- `POST /api/line/reputation-summary`

## 1. 建立 `.env`

PowerShell：

```powershell
Copy-Item .env.example .env
notepad .env
```

填入 LINE 與 BI-RMP 的實際值。

可用 PowerShell 產生 n8n encryption key：

```powershell
[Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

## 2. 先啟動 BI-RMP Backend

若 Backend 在 Windows 本機使用 8000 port：

```powershell
curl.exe http://localhost:8000/health
```

容器中的 n8n 會透過：

```text
http://host.docker.internal:8000
```

連回 Windows 本機 Backend。

## 3. 啟動 n8n

```powershell
docker compose pull
docker compose up -d n8n
docker compose ps
docker compose logs -f n8n
```

瀏覽器開啟：

```text
http://localhost:5678
```

第一次進入時建立 n8n 管理者帳號。

## 4. 匯入 workflow

命令列匯入：

```powershell
docker compose exec n8n n8n import:workflow --input=/workflows/line-reputation-summary.json
```

匯入後重新整理 n8n，開啟：

`LINE Reviews Enriched - Client Registration + Business Recognition`

匯入後預設為未啟用，先檢查節點，再按右上角 Publish/Active。

## 5. 開啟臨時 HTTPS Tunnel

```powershell
docker compose --profile tunnel up -d
docker compose logs -f cloudflared
```

紀錄日誌中的網址，例如：

```text
https://example-random.trycloudflare.com
```

正式 webhook URL 為：

```text
https://example-random.trycloudflare.com/webhook/line/events
```

測試 webhook URL 為：

```text
https://example-random.trycloudflare.com/webhook-test/line/events
```

Quick Tunnel 每次重建可能產生不同網址；只適合本機開發測試。

## 6. LINE Developers 設定

進入 Messaging API channel：

1. Webhook URL 填入 `https://...trycloudflare.com/webhook/line/events`
2. 按 Verify
3. 開啟 Use webhook
4. 建議測試階段關閉 LINE Official Account Manager 的自動回應，避免同時回兩次

## 7. 驗證

1. n8n workflow 必須 Active/Published。
2. 用手機傳文字給 LINE 官方帳號。
3. n8n 開啟 Executions。
4. 正常順序應為：
   - LINE Webhook
   - Verify Signature and Extract Events
   - Register LINE Client and Recognize Business
   - Get Global Reviews Enriched Report
   - Reply LINE User

## 8. 常用排錯

```powershell
# 檢查容器
docker compose ps

# n8n 日誌
docker compose logs --tail=200 n8n

# Tunnel 日誌
docker compose logs --tail=200 cloudflared

# 檢查環境變數是否進入容器（不要把輸出貼到公開場合）
docker compose exec n8n printenv | Select-String "LINE_|BI_RMP_|NODE_FUNCTION|N8N_BLOCK"

# 重啟
docker compose restart n8n

# 停止但保留資料
docker compose --profile tunnel down

# 完全刪除 n8n 資料（危險）
# docker compose --profile tunnel down -v
```

## 9. 常見錯誤對照

- `crypto is not allowed`：確認 `NODE_FUNCTION_ALLOW_BUILTIN=crypto`，重建 n8n。
- `access to env vars denied`：確認 `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`，重建 n8n。
- `ECONNREFUSED host.docker.internal:8000`：Backend 沒啟動、port 錯誤或只監聽 `127.0.0.1`。可讓 uvicorn 使用 `--host 0.0.0.0 --port 8000`。
- LINE Verify 失敗：確認 Tunnel 正常、URL 使用 HTTPS、workflow 已 Active，路徑是 `/webhook/line/events`。
- LINE 收到維護訊息：通常是兩支 Backend API 其中一支回傳錯誤，查看 n8n execution 的 HTTP Request 節點輸出。
