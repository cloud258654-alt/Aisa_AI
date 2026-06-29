# Sentinel ECXIP i18n 國際化指南

## 概述

Sentinel ECXIP 支援多語系介面，採用前端 i18n 框架實作。預設支援：
- **zh-TW** (繁體中文)
- **en-US** (英文)

---

## 架構

```
frontend/i18n/
├── index.js      # I18n 引擎 (t() 函數、語系切換、localStorage)
├── zh-TW.js      # 繁體中文翻譯字典 (260+ keys)
└── en-US.js      # 英文翻譯字典 (260+ keys)
```

### 核心函數

| 函數 | 說明 |
|------|------|
| `I18n.t(key, params)` | 取得翻譯文字，支援 `{{param}}` 變數替換 |
| `I18n.setLocale(locale)` | 切換語系 (zh-TW / en-US) |
| `I18n.getLocale()` | 取得目前語系 |
| `I18n.init(options)` | 初始化 i18n 引擎 |
| `I18nEvents.on(event, fn)` | 監聽語系變更事件 |
| `I18nEvents.emit(event, data)` | 觸發語系變更事件 |

---

## 如何新增語言

1. 建立新翻譯檔 `frontend/i18n/{locale}.js`
   ```javascript
   var I18nKoKR = {
     "nav.dashboard": "브랜드 대시보드",
     "nav.execBrief": "경영 브리핑",
     // ... 完整翻譯所有 key
   };
   ```

2. 在 `index.html` 加入 script 引用：
   ```html
   <script src="../i18n/ko-KR.js"></script>
   ```

3. 在 `app.js` 的 `I18n.init()` 中註冊：
   ```javascript
   I18n.init({
     defaultLocale: 'zh-TW',
     zhTW: I18nZhTW,
     enUS: I18nEnUS,
     koKR: I18nKoKR
   });
   ```

4. 更新 Language Switcher (`languageSwitcher.js`) 加入新語言選項。

---

## 如何新增翻譯 Key

### 在 HTML 中使用 (靜態文字)
```html
<span data-i18n="dashboard.brandHealth">品牌健康度</span>
```

### 在 HTML 中使用 (placeholder)
```html
<input data-i18n-placeholder="header.searchPlaceholder" placeholder="搜尋...">
```

### 在 HTML 中使用 (title 屬性)
```html
<button data-i18n-title="executive.refresh" title="重新整理">
```

### 在 JavaScript 中使用 (動態文字)
```javascript
el.textContent = I18n.t('voc.processReview');
// 帶參數
el.textContent = I18n.t('dashboard.riskValue', { value: 42 });
```

### 新增 Key 到翻譯檔
同時在 `zh-TW.js` 和 `en-US.js` 中加入對應 key：
```javascript
// zh-TW.js
"newSection.title": "新區塊標題",

// en-US.js
"newSection.title": "New Section Title",
```

---

## 如何切換語言

### 使用者操作
點擊 Header 右上角的語言切換器 (`繁中` / `EN`)。

### 程式化切換
```javascript
I18n.setLocale('en-US');
// 觸發 localeChanged 事件，自動重新渲染所有 i18n 元素
```

---

## localStorage 設定

| Key | 值 | 說明 |
|-----|-----|------|
| `sentinel-locale` | `zh-TW` 或 `en-US` | 使用者選擇的語系，頁面刷新後保留 |

---

## Fallback 規則

當找不到翻譯 key 時，依以下優先順序回退：
1. 找到指定語系的翻譯 → 直接使用
2. 若找不到 → 使用 `en-US` 翻譯
3. 若 en-US 也沒有 → 顯示原始 key 名稱 (不會造成畫面錯誤)

---

## 翻譯 Key 命名規範

使用點號分隔的階層式命名：

```
{domain}.{section}.{element}
```

範例：
- `nav.dashboard` — 導覽區 > 儀表板
- `dashboard.brandHealth` — 儀表板 > 品牌健康度
- `voc.processReview` — VOC > 處理輿情按鈕
- `modal.assignSop` — 彈窗 > 指派 SOP 按鈕

命名階層：
```
nav.*         導覽列
sidebar.*     側邊欄
header.*      頂部欄
dashboard.*   儀表板指標
executive.*   晨報決策中心
storeRanking.* 門市排行
predictions.* 預測中心
learning.*    學習記憶
voc.*         即時串流
journey.*     顧客旅程
ai.*          AI Brand Manager
sandbox.*     分析沙盒
modal.*       彈窗
risk.*        風險等級
store.*       門市狀態
trend.*       趨勢方向
common.*      通用文字
```

---

## 注意事項

1. **HTML 中的 data-i18n 文字作為 fallback**：即使 i18n 載入失敗，HTML 中的原始中文仍會顯示。
2. **動態產生的文字**：需在 component JavaScript 中使用 `I18n.t()` 取得翻譯。
3. **重新渲染**：語系切換時，動態內容需要重新渲染。監聽 `I18nEvents.on('localeChanged')` 事件。
4. **Mock 資料**：AI 摘要等 mock 資料目前以中文為主，英文版會顯示對應的英文摘要。
5. **不要硬編碼文字**：所有 UI 文案必須集中在翻譯檔中，不可寫死在元件內。
