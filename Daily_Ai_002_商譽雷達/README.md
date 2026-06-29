# Sentinel AI - Enterprise Customer Experience Intelligence Platform (ECXIP)

## 📌 專案簡介
本專案為 **Sentinel AI 顧客體驗智慧平台 (ECXIP) Phase 1 MVP**。
專案核心目標是建立高質感的單頁式決策儀表板 (SPA)，整合品牌聲量、顧客旅程摩擦診斷、即時輿情串流分析以及 AI 決策支援系統，展示如何利用 AI 自動追蹤、分析並提供品牌改善決策。

---

## 🚀 已完成功能說明

### 1. 品牌數據監控看板 (Brand Cockpit)
- **Brand Health Score (品牌健康度)**、**Store Health Index (門市健康指數)**、**CSAT (顧客滿意度)**、**Crisis Resolution Rate (危機解決率)**。
- 整合 **Reputation Risk Score (商譽風險指標)**，風險等級會根據輿情事件動態更新（Green 低風險 ➔ Amber 中風險 ➔ Crimson 臨界危機）。

### 2. 輿情聲量即時串流 (Voice Stream)
- 模擬即時滾動的顧客評論串流，管道包含：`Google Reviews`、`Threads`、`Facebook`、`Instagram`、`PTT`、`Dcard`。
- 每一則評論皆包含 AI 即時解析標籤：情感分析（Sentiment）、細粒度情緒（Emotion）、旅程觸點分類（Topic）、所屬分店與風險評估。
- 支援「暫停/啟動串流」、「清除串流」與「處理輿情」彈窗互動。

### 3. 顧客體驗旅程診斷 (Customer Journey Map)
- 視覺化顧客旅程（Search 搜尋 ➔ Book 預約 ➔ Wait 候位 ➔ Service 服務 ➔ Pay 結帳 ➔ Review 評論）。
- 動態顯示旅程節點指標與摩擦警示（如信義旗艦店的候位與服務節點出現異常警報）。
- 支援下拉選單篩選分店，儀表板指標與旅程圖表會即時連動切換。

### 4. AI 品牌經理決策終端 (AI Brand Manager Terminal)
- **指令模擬**：提供三組預設品牌危機事件（Threads 食安謠言、Google 排隊糾紛、PTT 服務投訴）觸發按鈕。
- 點擊後會在虛擬終端機中打印 AI 分析日誌，並產生專屬決策模組：
  - **Root Cause (原因解析)**：交叉分析社群與內部 POS 數據的根本原因。
  - **Operational SOP (改善流程)**：生成門市的待辦勾選清單，當清單全部勾選完成後，系統指標會自動修復。
  - **PR Statement (公關回應)**：自動生成公關回應範本，支援「一鍵複製」與「發布模擬」。
  - **Legal & Training (法務與培訓)**：提供法務避險建議與分店員工再培訓重點。

### 5. AI 語意分析沙盒 (NLP Sandbox)
- 互動式 NLP 遊樂場，使用者可輸入任何評論文字（或點選「填入示範負評」），點擊分析後將播放掃描動畫並顯示：
  - 情感分析（Sentiment Badge）
  - 情緒分析（Emotion）
  - 旅程痛點定位（Touchpoint）
  - 系統風險權重（Risk Index）
  - 自動生成對應的 PR 回覆草稿與門市營運 SOP 改善建議。

---

## 📂 專案檔案結構
```bash
d:/Ai study/Aisa_AI/Daily_Ai_002_商譽雷達/
├── 01_Project_Overview.md  # 專案願景與規劃說明文件
├── README.md               # 本接手與部署說明文件 (Handover Doc)
├── index.html              # 儀表板架構 (含語意標籤、SVG 圖示與彈窗模組)
├── index.css               # 視覺系統 (玻璃擬態、霓虹燈校準、響應式排版與動畫特效)
└── app.js                  # 核心邏輯 (串流引擎、動態指標換算、模擬分析器與交互事件)
```

---

## 💻 本地啟動與運行方式
本專案採用純前端架構，無須複雜的建置工具即可快速運行：
1. **使用 Python 啟動伺服器**：
   在專案根目錄下執行以下指令：
   ```powershell
   python -m http.server 8000
   ```
2. **在瀏覽器查看**：
   開啟瀏覽器並造訪 [http://localhost:8000](http://localhost:8000)。

---

## 🛠️ 接手開發建議 (Phase 2 路線圖)
後續接手夥伴（Opencode）可優先朝以下方向擴展：
1. **實接真實 API**：
   - 將 `app.js` 的 `reviewBank` 串接後端網路爬蟲 API（例如透過 Python FastAPI 爬取 Google Map / Threads / PTT 輿情）。
2. **大語言模型 (LLM) 整合**：
   - 沙盒分析（`btn-sandbox-analyze`）目前使用規則判斷，後續可串接 Gemini API，利用 Prompt 進行真實的 JSON 語意情感分析及 PR 生成。
3. **數據持久化與報表**：
   - 整合資料庫（如 PostgreSQL / Supabase）儲存歷史輿情與 SOP 執行紀錄。
   - 引入 Chart.js 將 Cockpit Metrics 繪製成歷史趨勢折線圖。
4. **多語系支援**：
   - 目前語系為繁體中文，可進一步擴增英文與其他亞洲語系。
