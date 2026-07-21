---
plan_id: "007"
title: "Markdown 文件中心與所見即所得介面"
status: "planned"
depends_on: ["004"]
format_version: 1
last_updated: "2026-07-21"
---

# 007 — Markdown 文件中心與所見即所得介面

## 目標

所有系統規格、計畫、操作手冊及驗收文件以 Markdown 儲存，並提供一般使用者可閱讀的所見即所得介面。

## 儲存原則

### 開發計畫文件

唯一來源：

```text
Daily_Ai_004_Futain0857 system/docs/
```

Git 管理版本，不在 Google Sheets 儲存完整 Markdown 內容。

### 系統內可編輯文件

若後續需要讓管理員從系統編輯文件：

- 內容仍儲存為純 `.md`。
- 透過 GAS `DriveApp` 儲存在指定 Google Drive 資料夾。
- Script Property 使用：

```text
DOCUMENTS_FOLDER_ID
```

- Google Sheets 僅保存索引及 Metadata，不保存大量正文。

建議索引工作表：

```text
documents_index
```

欄位：

```text
document_id
slug
title
category
drive_file_id
status
version
updated_by
created_at
updated_at
```

## Markdown 格式規範

每份文件使用 YAML Front Matter：

```yaml
---
document_id: "DOC-001"
title: "客戶操作手冊"
category: "user-manual"
status: "published"
version: 1
updated_at: "2026-07-21T12:00:00+08:00"
---
```

正文支援：

- 標題
- 段落
- 粗體、斜體
- 有序及無序清單
- Task list
- 表格
- 引用
- 程式碼區塊
- 連結
- 圖片
- Mermaid 流程圖

原始 HTML 預設禁用，避免 XSS。

## 使用者介面

新增路由：

```text
/docs
/docs/:slug
/docs/:slug/edit
```

### 文件清單

- 分類
- 搜尋
- 狀態
- 最後更新時間
- 版本
- 只顯示已發布文件給一般操作者

### 閱讀模式

- 將 Markdown 渲染為乾淨的文章版面。
- 支援目錄 TOC。
- Mermaid 圖表。
- 程式碼 Highlight。
- 列印樣式。
- 手機 RWD。
- 深藍、金色品牌樣式。

### 編輯模式

管理員可切換：

```text
WYSIWYG
Markdown Source
Split Preview
```

必要功能：

- 標題及段落
- 清單及 Task list
- 表格
- 連結
- 圖片
- 程式碼
- Undo／Redo
- 儲存草稿
- 預覽
- 發布
- 未儲存離開警告

技術選型先做 Spike：

1. 優先評估 `MDXEditor`，因其為 React 的 WYSIWYG Markdown 編輯元件。
2. 備選 `TOAST UI Editor`，其支援 Markdown 與 WYSIWYG 兩種模式。
3. 最終選擇須驗證：
   - React 18 + Vite 相容
   - 中文輸入
   - 表格及 Task list
   - 純 Markdown 往返不明顯失真
   - Bundle size
   - 無障礙
   - 自訂品牌樣式
   - Mermaid 整合

不得在完成 Spike 前同時安裝兩套編輯器到正式 Bundle。

## 建議元件

```text
src/pages/DocsPage.tsx
src/pages/DocDetailPage.tsx
src/pages/DocEditorPage.tsx

src/components/docs/
├── DocsSidebar.tsx
├── DocsSearch.tsx
├── MarkdownViewer.tsx
├── MarkdownEditor.tsx
├── TableOfContents.tsx
├── MermaidBlock.tsx
├── DocumentMetadata.tsx
└── PublishDialog.tsx

src/services/api/documentsApi.ts
src/types/document.ts
```

## 安全

- Markdown 渲染前 Sanitization。
- Raw HTML 預設關閉。
- 連結加入安全屬性。
- 圖片只允許 HTTPS 或受信來源。
- 管理員才可編輯及發布。
- API 不接受任意 Drive File ID。
- 檔名及 Slug 白名單驗證。
- 文件版本不可直接覆蓋，保存 Revision Metadata。

## API

```text
listDocuments
getDocument
createDocument
updateDocumentDraft
publishDocument
archiveDocument
getDocumentHistory
```

所有寫入接受 `requestId`。

## 開發文件預覽

在 Antigravity IDE／GitHub 中，`docs/plans/*.md` 可直接使用 Markdown Preview 閱讀。

若要在前端顯示 Repository 內建文件：

1. Build 前將指定 Markdown 複製到 `public/docs/`。
2. 禁止將本機絕對路徑寫入程式。
3. Build 產物只讀，不從前端回寫 GitHub。
4. 正式編輯文件使用 GAS + Drive 流程。

## 測試

- Markdown → WYSIWYG → Markdown 往返。
- 中文輸入法。
- 表格、Task list、程式碼及 Mermaid。
- XSS payload。
- 未儲存離開。
- 發布與草稿權限。
- 手機閱讀及編輯。
- 大型文件載入。
- Drive API 失敗。
- 重複 requestId。

## 驗收條件

- [ ] `docs/plans` 文件可直接 Markdown Preview。
- [ ] 系統 `/docs` 可閱讀 Markdown。
- [ ] TOC、表格、程式碼及 Mermaid 可渲染。
- [ ] 手機閱讀正常。
- [ ] Raw HTML 或惡意內容不被執行。
- [ ] WYSIWYG／Source／Split 模式至少完成兩種；MVP 必須有閱讀及 Source Preview。
- [ ] 若啟用編輯，可保存純 Markdown。
- [ ] 草稿、發布及版本 Metadata 可追蹤。
- [ ] Lint、test、build 通過。
- [ ] 使用方式加入操作手冊。

## MVP 與後續界線

### MVP 必須

- Repository Markdown 文件
- 文件清單
- 所見即所得閱讀渲染
- TOC、表格、Task list、Code、Mermaid
- 手機 RWD
- 安全 Sanitization

### 可延後

- 多人協作
- 即時共同編輯
- 評論
- 全文索引服務
- 文件審批工作流
- GitHub 直接回寫
- AI 文件摘要

## Antigravity IDE 執行指令

```text
先完成 Markdown 文件閱讀中心及技術 Spike。
比較 MDXEditor 與 TOAST UI Editor，但正式程式只選一套。
MVP 先確保純 Markdown 儲存、WYSIWYG 閱讀、Source Preview、
GFM 表格／Task list、Mermaid 及安全 Sanitization。
若 Drive 寫入尚未部署，編輯模式可先使用測試 Adapter，
不得假裝已永久保存。
```
