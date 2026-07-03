# PTT Joke Meme PWA — Cloud AI SDS 範例

## 說明

本專案為 Cloud AI Software Development Standard (Cloud AI SDS) 的實際應用範例。

## SDS 應用

| SDS 標準 | 本專案實作 |
|----------|-----------|
| Project Template | 採用 SDS Project_Template 目錄結構 |
| AI Collaboration Standard | 三 AI 分工（OpenCode / Gemini / Codex） |
| Documentation Standard | 依規範建立 docs/ 與 ai_collaboration/ 文件 |
| Review Standard | Codex 負責程式碼審查 |
| SDD Template | 設計文件依 SDS SDD 格式撰寫 |
| Requirement Template | 需求規格依 SDS Requirement 格式撰寫 |
| API Template | API 設計依 SDS API 格式撰寫 |

## 目錄結構

```
docs/               # 專案文件（依 SDS Documentation Standard）
ai_collaboration/   # AI 協作文件（依 SDS AI Collaboration Standard）
backend/            # FastAPI 後端（OpenCode 負責）
frontend/           # PWA 前端（Gemini 負責）
database/           # SQLite / SQLAlchemy（OpenCode 負責）
tests/              # 測試
scripts/            # 工具腳本
```

## 團隊分工

| 角色 | Agent | 責任 |
|------|-------|------|
| Backend | OpenCode | 後端、爬蟲、資料庫、API |
| Frontend | Gemini | 前端、PWA、RWD、UI |
| Reviewer | Codex | 程式碼審查 |

## 相關文件

- `docs/01_Project_Overview.md`
- `docs/02_Requirements.md`
- `docs/03_Software_Design.md`
- `docs/CHANGELOG.md`
- `ai_collaboration/AGENT_BOUNDARY.md`
- `ai_collaboration/CURRENT_TASK.md`
- `ai_collaboration/TASK_ASSIGNMENT.json`
- `ai_collaboration/HANDOVER.md`
