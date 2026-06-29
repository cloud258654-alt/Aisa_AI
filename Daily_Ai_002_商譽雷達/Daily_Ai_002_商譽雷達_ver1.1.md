# Sentinel AI 顧客體驗智慧平台 (ECXIP) 進度報告 - Ver 1.1

本報告記錄截至 2026-06-29 時，**Daily_Ai_002_商譽雷達** 專案的開發進度、現有架構、檔案清單以及後續接手（Opencode）之開發規劃。

---

## 📌 專案基本資訊
- **專案名稱**：Sentinel AI Enterprise Customer Experience Intelligence Platform (ECXIP)
- **版本編號**：Ver 1.1 (Phase 1 MVP - 品牌監控與 AI 分析)
- **視覺風格**：Apple 官方質感之「玻璃透白」（Frosted Light-mode）設計
- **預覽網址**：`http://localhost:26117` (或預設 Python 本地伺服器 `http://localhost:8000`)
- **GitHub 儲存庫**：[Aisa_AI](https://github.com/cloud258654-alt/Aisa_AI)

---

## 🚀 目前完成項目 (Ver 1.1 功能清單)

### 1. 品牌決策 cockpit 看板
- 整合 **Brand Health Score (品牌健康度)**、**Store Health Index (門市健康指數)**、**CSAT (顧客滿意度)**、**Crisis Resolution Rate (危機解決率)** 四大圓環指標。
- 整合 **Reputation Risk Score (商譽風險值)** 等級指示條，依據輿情危機程度動態變換顏色（綠色低風險 ➔ 橘色中風險 ➔ 紅色極度危機）。
- 指標會隨著實時輿情事件或沙盒分析結果動態浮動，提供真實的指標回饋感。

### 2. 輿情聲量即時串流 (Voice Stream)
- 模擬即時滾動的顧客評論，渠道包含 `Google Reviews`、`Threads`、`Facebook`、`Instagram`、`PTT`、`Dcard`。
- 每則評論自動透過 AI pipeline 進行情感分析（Sentiment）、情緒識別（Emotion）、旅程觸點（Topic）、所屬分店與風險權重標記。
- 點擊「處理輿情」按鈕會開啟彈窗，提供 SOP 指派、AI 回覆產出、公關上報等模擬操作，完成後可提昇品牌滿意度並降低風險。

### 3. 顧客體驗旅程診斷 (Customer Journey Map)
- 視覺化顾客旅程（搜尋 ➔ 預約 ➔ 候位 ➔ 服務 ➔ 結帳 ➔ 評論）。
- 當特定節點出現摩擦時（例如等候時間過長、服務態度不佳），節點會顯示 Amber (黃色警告) 或 Crimson (紅色警報) 並持續閃爍，並在下方列出詳細的診斷卡片。
- 支持分店切換篩選，可獨立查看信義店、忠孝店、板橋店、台中店的旅程診斷。

### 4. AI 專屬 Brand Manager (決策指揮中心)
- 提供三組預設品牌危機模擬按鈕（Threads 食安謠言、Google 排隊糾紛、PTT 服務投訴）。
- 點選後虛擬終端會以擬真延遲打印 AI 搜集分析日誌，並產生專屬分頁應變模組：
  - **Root Cause (原因解析)**：比對內部 POS 數據及監視器，定位流程摩擦。
  - **Operational SOP (改善流程)**：提供交互式待辦清單，當清單全數被勾選後，品牌指標將自動修復。
  - **PR Statement (公關回應)**：擬定官方聲明，支持一鍵複製與 Threads/Google/PTT 一鍵張貼模擬。
  - **Legal & Training (法務與培訓)**：提供法務避險建議與門市員工再培訓口訣。

### 5. AI 語意分析沙盒 (NLP Sandbox)
- 開放輸入自定義的評論文字，點擊「執行 AI 深度分析」後，會撥放科技感的光線掃描動畫，並即時提取：
  - 情感分析結果與信心度
  - 細粒度情緒 (喜悅、憤怒、無奈、好奇等)
  - 旅程定位與商譽風險等級
  - 自動生成對應的 PR 官方回覆範本與門市營運 SOP 改善建議。

---

## 📂 專案檔案清單與路徑
```bash
Daily_Ai_002_商譽雷達/
├── 01_Project_Overview.md             # 專案 Phase 1 ~ 4 願景與 MVP 目標規劃書
├── README.md                          # 專案基本部署與 Phase 2 開發交接手冊
├── Daily_Ai_002_商譽雷達_ver1.1.md   # 本次進度報告與架構總覽 (本檔案)
├── index.html                         # 單頁式應用主架構 (HTML5 + SVG)
├── index.css                          # Apple 官網玻璃透白風樣式系統 (Frosted glass & transitions)
└── app.js                             # 數據串流、指標引擎、分析沙盒與危機模擬邏輯
```

---

## 🛠️ 下階段 (Phase 2) 接手開發建議
後續接手夥伴（Opencode）可優先規劃以下核心板塊的實作：
1. **真實輿情爬蟲對接**：
   - 建立 Python (FastAPI) 後端，串接 Google Map / Threads / Dcard API。
   - 將 `app.js` 的模擬串流替換為真實的 Server-Sent Events (SSE) 或 WebSocket 實時推送。
2. **真實大模型 (LLM) 分析**：
   - 串接 Google Gemini API / OpenAI API。
   - 將沙盒輸入的文字以 Prompt 送交 LLM，回傳結構化的 JSON，以進行真實的情感、情緒提取與營運 SOP 推薦。
3. **歷史報表與數據可視化**：
   - 整合 PostgreSQL 資料庫，記錄歷史聲量趨勢。
   - 引入 Chart.js / D3.js，將 Cockpit 的 Brand Score 等指標繪製成歷史趨勢圖表。
