// Sentinel AI Enterprise Customer Experience Intelligence Platform (ECXIP)
// Core Application Logic

// System Time Auto-update
function updateSystemTime() {
    const timeEl = document.getElementById('system-time');
    if (!timeEl) return;
    const now = new Date();
    // Simulate beginning from the user's standard baseline or real current time
    const format = now.getFullYear() + '-' + 
                   String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                   String(now.getDate()).padStart(2, '0') + ' ' + 
                   String(now.getHours()).padStart(2, '0') + ':' + 
                   String(now.getMinutes()).padStart(2, '0') + ':' + 
                   String(now.getSeconds()).padStart(2, '0');
    timeEl.textContent = format;
}
setInterval(updateSystemTime, 1000);
updateSystemTime();

// Active Metrics Baseline State
let metrics = {
    brandScore: 92.4,
    storeHealth: 98.1,
    csat: 4.82,
    resolutionRate: 94.5,
    riskScore: 12
};

// Store Filtering Behaviour
const storeFilter = document.getElementById('store-filter');
if (storeFilter) {
    storeFilter.addEventListener('change', (e) => {
        const val = e.target.value;
        const detailsContainer = document.getElementById('journey-details');
        const nodeWait = document.getElementById('node-wait');
        const nodeService = document.getElementById('node-service');
        const scoreWait = document.getElementById('node-score-wait');
        const scoreService = document.getElementById('node-score-service');

        if (val === 'all' || val === 'xinyi') {
            // Restore friction in Xinyi
            nodeWait.className = "journey-node warning";
            nodeService.className = "journey-node error";
            scoreWait.textContent = "84%";
            scoreService.textContent = "79%";
            detailsContainer.innerHTML = `
                <div class="diagnostic-card warning">
                    <div class="diag-header">
                        <span class="diag-title">候位到店摩擦 (等候時間過長)</span>
                        <span class="store-tag">信義旗艦店</span>
                    </div>
                    <p class="diag-desc">最近 48 小時有 18 則負評提及「排隊引導混亂、候位時間超過預期」。AI 偵測流程流失率上升 4.2%。</p>
                </div>
                <div class="diagnostic-card error">
                    <div class="diag-header">
                        <span class="diag-title">服務體驗摩擦 (出餐速度及服務態度)</span>
                        <span class="store-tag">信義旗艦店</span>
                    </div>
                    <p class="diag-desc">輿情中提及「出餐送錯、主餐冷掉、員工態度冷淡」之關鍵字密度暴增 320%。品牌健康度主要扣分項。</p>
                </div>
            `;
            updateDashboardMetrics(92.4, 98.1, 4.82, 94.5, 12);
        } else if (val === 'zhongxiao') {
            // SOGO branch is completely healthy
            nodeWait.className = "journey-node active";
            nodeService.className = "journey-node active";
            scoreWait.textContent = "97%";
            scoreService.textContent = "96%";
            detailsContainer.innerHTML = `
                <div class="diagnostic-card" style="background-color: rgba(16, 185, 129, 0.03); border-color: rgba(16, 185, 129, 0.15); grid-column: span 2;">
                    <div class="diag-header">
                        <span class="diag-title" style="color: var(--accent-emerald)">忠孝 SOGO 店營運狀態良好</span>
                        <span class="store-tag">忠孝 SOGO 店</span>
                    </div>
                    <p class="diag-desc">所有顧客旅程節點 (Search ➔ Review) 指標均高於 95% 門檻。本週滿意度維持高點，無顯著客訴事件。</p>
                </div>
            `;
            updateDashboardMetrics(96.8, 99.5, 4.91, 98.0, 5);
        } else {
            // Other branches healthy
            nodeWait.className = "journey-node active";
            nodeService.className = "journey-node active";
            scoreWait.textContent = "95%";
            scoreService.textContent = "94%";
            detailsContainer.innerHTML = `
                <div class="diagnostic-card" style="background-color: rgba(255,255,255,0.02); border-color: var(--border-color); grid-column: span 2;">
                    <div class="diag-header">
                        <span class="diag-title">門市健康度分析</span>
                        <span class="store-tag">分店診斷</span>
                    </div>
                    <p class="diag-desc">該門市目前數據平穩。點選其他門市或返回「全品牌門市」以查看整體輿情走勢。</p>
                </div>
            `;
            updateDashboardMetrics(94.2, 98.7, 4.85, 96.0, 8);
        }
    });
}

function updateDashboardMetrics(brand, store, csat, res, risk) {
    metrics = { brandScore: brand, storeHealth: store, csat: csat, resolutionRate: res, riskScore: risk };
    
    // Update elements
    document.getElementById('val-brand-score').textContent = brand.toFixed(1);
    document.getElementById('val-store-health').textContent = store.toFixed(1) + '%';
    document.getElementById('val-csat').innerHTML = csat.toFixed(2) + ' <span class="max-val">/ 5</span>';
    document.getElementById('val-resolution').textContent = res.toFixed(1) + '%';
    
    const riskEl = document.getElementById('val-risk');
    const riskBar = document.getElementById('risk-bar');
    
    riskBar.style.width = risk + '%';
    
    if (risk < 30) {
        riskEl.textContent = `Low (${risk})`;
        riskEl.className = "metric-value text-green";
    } else if (risk < 70) {
        riskEl.textContent = `Medium (${risk})`;
        riskEl.className = "metric-value text-amber";
    } else {
        riskEl.textContent = `CRITICAL (${risk})`;
        riskEl.className = "metric-value text-rose";
    }
    
    // Update circles
    document.getElementById('circle-brand-score').setAttribute('stroke-dasharray', `${brand}, 100`);
    document.getElementById('circle-store-health').setAttribute('stroke-dasharray', `${store}, 100`);
    document.getElementById('circle-csat').setAttribute('stroke-dasharray', `${(csat/5)*100}, 100`);
    document.getElementById('circle-resolution').setAttribute('stroke-dasharray', `${res}, 100`);
}

// Simulated Reputation Reviews Bank
const reviewBank = [
    {
        channel: 'google',
        channelName: 'Google Maps 評論',
        author: '張*豪',
        text: '這家信義店的服務態度真的很不ok，點完餐等了30分鐘才說漏單，最後送上來的牛排還是溫冷的...真的不會再來第二次了。',
        sentiment: 'negative',
        emotion: 'Anger 😠',
        topic: '服務態度 / 出餐速度',
        store: '信義旗艦店',
        risk: 'mid'
    },
    {
        channel: 'threads',
        channelName: 'Threads',
        author: 'charlie_daily',
        text: '剛剛在忠孝店吃飯，隔壁桌的客人居然為了排隊順序跟店員大吵，店長處理速度很快，主動送了兩張折價券把人安撫走，危機處理給過！👍',
        sentiment: 'positive',
        emotion: 'Delight 😄',
        topic: '客訴處理',
        store: '忠孝 SOGO 店',
        risk: 'low'
    },
    {
        channel: 'ptt',
        channelName: 'PTT Food 版',
        author: 'windrider',
        text: '[食記] 台中公益店新菜單體驗！極黑和牛拼盤份量很多，肉質很棒，服務人員烤肉技巧很好，雖然價格偏高但非常推薦家庭聚餐。',
        sentiment: 'positive',
        emotion: 'Trust 🤝',
        topic: '食材品質 / 服務體驗',
        store: '台中公益店',
        risk: 'low'
    },
    {
        channel: 'facebook',
        channelName: 'Facebook Page',
        author: '林秀琴',
        text: '打電話去預約板橋店，接電話的服務生態度愛理不理的，問他有沒有包廂也講不清楚，到底有沒有受過員工訓練啊？',
        sentiment: 'negative',
        emotion: 'Frustration 😩',
        topic: '預約系統 / 員工訓練',
        store: '板橋大遠百店',
        risk: 'mid'
    },
    {
        channel: 'instagram',
        channelName: 'Instagram Tag',
        author: 'yuki_travel',
        text: '新裝潢的信義旗艦店超美！霓虹燈區隨便拍都超有質感，點了限定的芒果聖代也很好吃，大推週末跟閨蜜一起來約會打卡📸✨',
        sentiment: 'positive',
        emotion: 'Joy 😊',
        topic: '店面裝潢 / 甜點品質',
        store: '信義旗艦店',
        risk: 'low'
    },
    {
        channel: 'dcard',
        channelName: 'Dcard 美食板',
        author: '逢甲小食神',
        text: '有人吃過這家的台中公益店嗎？聽說最近尖峰時間排隊要等快兩個小時，不知道值不值得排？還是有推薦比較不擠的時段？',
        sentiment: 'neutral',
        emotion: 'Curiosity 🤔',
        topic: '候位時間',
        store: '台中公益店',
        risk: 'low'
    },
    {
        channel: 'google',
        channelName: 'Google Maps 評論',
        author: 'Elena Wang',
        text: '今天去用餐，點餐APP一直當機跑不出條碼，結帳的櫃檯只有開一個，大排長龍，希望可以儘快更新系統。',
        sentiment: 'negative',
        emotion: 'Frustration 😩',
        topic: '硬體系統 / 結帳流程',
        store: '信義旗艦店',
        risk: 'low'
    },
    {
        channel: 'threads',
        channelName: 'Threads',
        author: 'jessica_w',
        text: '笑死，這家台北店又被爆出服務生臉很臭，但我每次去都覺得還好耶？果然評論都看看就好，還是自己吃過最準。',
        sentiment: 'neutral',
        emotion: 'Neutral 😐',
        topic: '服務態度',
        store: '信義旗艦店',
        risk: 'low'
    }
];

// Live stream execution logic
let streamInterval = null;
let isStreamRunning = true;
const streamContainer = document.getElementById('stream-feed-container');

function createVoiceCard(data, isPrepend = true) {
    const card = document.createElement('div');
    card.className = `voice-item`;
    
    const riskBadge = data.risk === 'high' ? `<span class="v-badge risk-high">High Risk Alert</span>` : '';
    const sentimentClass = data.sentiment;
    
    card.innerHTML = `
        <div class="voice-meta">
            <div class="channel-tag ${data.channel}">
                <span class="channel-dot ${data.channel}"></span>
                <span>${data.channelName} (@${data.author})</span>
            </div>
            <span class="voice-time">剛剛</span>
        </div>
        <p class="voice-body">${data.text}</p>
        <div class="voice-tags">
            <span class="v-badge ${sentimentClass}">${data.sentiment.toUpperCase()}</span>
            <span class="v-badge topic">${data.topic}</span>
            <span class="v-badge store">${data.store}</span>
            ${riskBadge}
        </div>
        <div class="voice-actions">
            <button class="btn-sm btn-sm-primary btn-process-review">處理輿情</button>
        </div>
    `;
    
    if (isPrepend) {
        streamContainer.prepend(card);
    } else {
        streamContainer.appendChild(card);
    }
    
    // Bind action button
    const processBtn = card.querySelector('.btn-process-review');
    processBtn.addEventListener('click', () => {
        openModal(data.text);
    });
    
    // Prune excessive elements
    if (streamContainer.children.length > 20) {
        streamContainer.removeChild(streamContainer.lastChild);
    }
}

// Initial Population
function initStream() {
    // Show some initial items
    for (let i = 0; i < 5; i++) {
        const mockItem = reviewBank[Math.floor(Math.random() * reviewBank.length)];
        createVoiceCard(mockItem, false);
    }
    
    // Set up continuous feeding
    startStreamInterval();
}

function startStreamInterval() {
    if (streamInterval) clearInterval(streamInterval);
    
    streamInterval = setInterval(() => {
        if (!isStreamRunning) return;
        
        // Randomly pick a review from the bank
        const randomReview = {...reviewBank[Math.floor(Math.random() * reviewBank.length)]};
        
        // Give random authors and slight variations to look real
        randomReview.author = ['陳*美', '王*明', 'Li_99', 'abby_c', 'justin_t', '吳*華'][Math.floor(Math.random() * 6)];
        
        createVoiceCard(randomReview, true);
        
        // Dynamic impact on dashboard metrics based on incoming feedback
        if (randomReview.sentiment === 'negative') {
            const newBrand = Math.max(80, metrics.brandScore - 0.2);
            const newCSAT = Math.max(4.0, metrics.csat - 0.01);
            const newRisk = Math.min(100, metrics.riskScore + 2);
            updateDashboardMetrics(newBrand, metrics.storeHealth, newCSAT, metrics.resolutionRate, newRisk);
        } else if (randomReview.sentiment === 'positive') {
            const newBrand = Math.min(100, metrics.brandScore + 0.1);
            const newCSAT = Math.min(5.0, metrics.csat + 0.005);
            const newRisk = Math.max(0, metrics.riskScore - 1);
            updateDashboardMetrics(newBrand, metrics.storeHealth, newCSAT, metrics.resolutionRate, newRisk);
        }
    }, 6000);
}

// Play/Pause stream toggle
const btnPause = document.getElementById('btn-pause-stream');
if (btnPause) {
    btnPause.addEventListener('click', () => {
        isStreamRunning = !isStreamRunning;
        if (isStreamRunning) {
            btnPause.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="pause-icon"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;
            btnPause.classList.remove('paused');
        } else {
            btnPause.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`;
            btnPause.classList.add('paused');
        }
    });
}

// Clear stream window
const btnClear = document.getElementById('btn-clear-stream');
if (btnClear) {
    btnClear.addEventListener('click', () => {
        streamContainer.innerHTML = '';
    });
}

// Modal Handler
const modal = document.getElementById('action-modal');
const modalClose = document.getElementById('modal-close');
const modalReviewText = document.getElementById('modal-review-text');

function openModal(text) {
    modalReviewText.textContent = text;
    modal.style.display = 'flex';
}

function closeModal() {
    modal.style.display = 'none';
}

if (modalClose) modalClose.addEventListener('click', closeModal);
window.addEventListener('click', (e) => {
    if (e.target === modal) {
        closeModal();
    }
});

// Modal action button triggers
const modalActions = ['modal-action-sop', 'modal-action-reply', 'modal-action-pr'];
modalActions.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('click', () => {
            closeModal();
            // Simulate resolution rate recovery
            const newRes = Math.min(100, metrics.resolutionRate + 0.5);
            const newRisk = Math.max(5, metrics.riskScore - 3);
            updateDashboardMetrics(metrics.brandScore, metrics.storeHealth, metrics.csat, newRes, newRisk);
            
            // Print action to terminal
            printTerminalLog('[SYSTEM]', `輿情處理指令已發出。操作類型：${el.textContent}。品牌指標已重新校準。`, 'success-msg');
        });
    }
});

// AI Command Center: Preset Crisis Actions
const terminal = document.getElementById('terminal-body');
const decisionOutputs = document.getElementById('decision-outputs');

function printTerminalLog(tag, msg, className = 'system-msg') {
    const now = new Date();
    const ts = `[${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}]`;
    const row = document.createElement('div');
    row.className = `terminal-row ${className}`;
    row.innerHTML = `<span class="timestamp">${ts}</span> ${tag} ${msg}`;
    terminal.appendChild(row);
    terminal.scrollTop = terminal.scrollHeight;
}

// Setup preset crisis scripts
const presetCrises = {
    threads: {
        command: "run-analysis --channel=threads --topic=food-safety --store=信義旗艦店",
        logs: [
            { tag: "[AGENT]", msg: "已鎖定 Threads 熱門貼文：'網友爆料信義店出餐海鮮有異味，疑似集體腹瀉。'", cls: "user-cmd" },
            { tag: "[AI ENGINE]", msg: "正在回溯最近 24 小時出餐紀錄... 查核當日有 289 份海鮮拼盤售出，店面回報無異常食材客訴。", cls: "system-msg" },
            { tag: "[AI ENGINE]", msg: "輿情情緒深度萃取：恐慌 (54%)、憤怒 (32%)。輿情擴散速率：極高 (12 貼文/小時)。", cls: "danger-msg" },
            { tag: "[AI ENGINE]", msg: "商譽危機預警觸發！風險分數升至 82 (CRITICAL)。建議啟動一級品牌應變指南。", cls: "danger-msg" },
            { tag: "[SYSTEM]", msg: "已生成 AI 決策支援模組 (原因解析/門市SOP/公關聲明/法務培訓)。", cls: "success-msg" }
        ],
        metrics: [85.5, 92.0, 4.35, 90.0, 82],
        outputs: {
            rootCause: `
                <div class="analysis-summary-block">
                    <span class="analysis-headline">Threads 食安謠言 - 原因追蹤</span>
                    <div class="analysis-points">
                        <div class="analysis-point-item"><strong>輿情源頭</strong> Threads 網友 @yummy_test 發文指稱「吃完回家拉肚子」，引發 150+ 轉發。</div>
                        <div class="analysis-point-item"><strong>內部數據</strong> 當日信義店食材留樣紀錄良好，冰箱溫度監控正常，但「海鮮送達至出餐」流程在尖峰段有 12 分鐘的室溫曝露空檔。</div>
                        <div class="analysis-point-item"><strong>診斷結論</strong> 雖無明確食物中毒科學證據，但出餐流暢度不足導致的餐點失溫，是造成顧客口感不佳與懷疑的主因。</div>
                    </div>
                </div>
            `,
            sop: `
                <ul class="sop-checklist">
                    <li class="sop-item"><input type="checkbox" id="t-sop-1"> <span>信義店海鮮食材改為「出餐前最後一刻自冷藏庫取出」，嚴禁提前置於室溫備餐。</span></li>
                    <li class="sop-item"><input type="checkbox" id="t-sop-2"> <span>店經理主動聯絡原貼文網友，詢問就醫證明並承諾全額負擔醫療費用，展現積極負責態度。</span></li>
                    <li class="sop-item"><input type="checkbox" id="t-sop-3"> <span>召回當天庫存食材，委託第三方公正機構進行自主檢驗 (大腸桿菌群、沙門氏菌)。</span></li>
                </ul>
            `,
            pr: `
                <div class="pr-block" id="pr-statement-text-t">
【品牌官方聲明】
針對今日網路社群提及信義店食材安全之疑慮，本公司高度重視。
本公司已於第一時間對信義店進行全面自主清查，當日冰箱溫度、人員衛生及留樣紀錄均符合標準。目前已主動聯繫發文顧客了解身體狀況，並同步將同批食材送往第三方檢驗。
我們深知食品安全為企業命脈，後續檢驗結果將公開透明說明。若同仁出餐速度與溫度有未達標準之處，我們深表歉意，並已啟動流程優化。
                </div>
                <div class="pr-actions">
                    <button class="btn btn-secondary btn-copy-pr" data-target="pr-statement-text-t">複製聲明</button>
                    <button class="btn btn-primary btn-publish-pr" data-type="Threads">一鍵張貼至 Threads</button>
                </div>
            `,
            legal: `
                <div class="legal-grid">
                    <div class="legal-box alert">
                        <h4>法務防線警示</h4>
                        <ul>
                            <li>保留當日發文截圖與後續傳播鏈，若證實屬同行惡意造謠，可依民法妨礙商譽求償。</li>
                            <li>聲明中切勿承諾「賠償一定金額」，需註明「協助釐清身體狀況及支付合理醫療費用」。</li>
                        </ul>
                    </div>
                    <div class="legal-box training">
                        <h4>門市再培訓要點</h4>
                        <ul>
                            <li>全體外場加強「異常餐點回收通報機制」，若顧客反應海鮮有異味，應立即撤餐並通報主管。</li>
                            <li>廚房幹部加強「冷鏈交接時間控管」教育訓練。</li>
                        </ul>
                    </div>
                </div>
            `
        }
    },
    google: {
        command: "run-analysis --channel=google --topic=queue-dispute --store=信義旗艦店",
        logs: [
            { tag: "[AGENT]", msg: "已分析 Google Maps 一星評論爆發：'候位人員引導插隊，現場爆發拉扯口角。'", cls: "user-cmd" },
            { tag: "[AI ENGINE]", msg: "比對現場監視器與 POS 紀錄... 當時候位人數 48 組，現場等候線混亂，動線與路人重合。", cls: "system-msg" },
            { tag: "[AI ENGINE]", msg: "負面情緒指標：Frustration (68%)。輿情擴散速率：中 (2 貼文/小時)。", cls: "warning-msg" },
            { tag: "[AI ENGINE]", msg: "商譽風險分數調升至 45 (Medium)。建議調整門市候位 SOP 並啟動補償機制。", cls: "warning-msg" },
            { tag: "[SYSTEM]", msg: "已生成 AI 決策支援模組 (原因解析/門市SOP/公關聲明/法務培訓)。", cls: "success-msg" }
        ],
        metrics: [89.8, 95.0, 4.60, 92.5, 45],
        outputs: {
            rootCause: `
                <div class="analysis-summary-block">
                    <span class="analysis-headline">Google 排隊糾紛 - 原因追蹤</span>
                    <div class="analysis-points">
                        <div class="analysis-point-item"><strong>輿情源頭</strong> 顧客投訴現場服務生「沒發號碼牌，讓後來的人先入座」，造成插隊誤會，引發多組顧客跟進洗負評。</div>
                        <div class="analysis-point-item"><strong>內部數據</strong> 當天信義店實施「APP與現場混合候位」，由於條碼掃描器故障，帶位同仁改採人工登記，因名單重疊導致順序出錯。</div>
                        <div class="analysis-point-item"><strong>診斷結論</strong> 軟硬體配套備援不足，加上尖峰時段現場無專門的排隊動線指引牌，導致顧客觀感極差。</div>
                    </div>
                </div>
            `,
            sop: `
                <ul class="sop-checklist">
                    <li class="sop-item"><input type="checkbox" id="g-sop-1"> <span>立即購置「實體紅龍排隊指引」，清楚區分「APP已報到區」與「現場登記區」。</span></li>
                    <li class="sop-item"><input type="checkbox" id="g-sop-2"> <span>當候位系統當機時，強制執行「三聯單手寫登記」，並主動向排隊顧客說明規則。</span></li>
                    <li class="sop-item"><input type="checkbox" id="g-sop-3"> <span>針對當場受排隊糾紛波及的顧客，由店長代表致歉並贈送茶點兌換券。</span></li>
                </ul>
            `,
            pr: `
                <div class="pr-block" id="pr-statement-text-g">
親愛的顧客您好，對於今日信義店現場排隊動線引導不佳、造成您用餐心情受影響，我們致上最深的歉意。
由於當天候位系統偶發故障，同仁切換手工作業時順序有誤，導致您的權益受損。我們已重新規劃現場紅龍指引與備援登記流程，並對當天帶位同仁加強現場溝通培訓。
我們非常希望能有機會聯絡您，提供後續補償，您的建議是我們持續進步的動力。
                </div>
                <div class="pr-actions">
                    <button class="btn btn-secondary btn-copy-pr" data-target="pr-statement-text-g">複製聲明</button>
                    <button class="btn btn-primary btn-publish-pr" data-type="Google">張貼回覆至 Google Review</button>
                </div>
            `,
            legal: `
                <div class="legal-grid">
                    <div class="legal-box alert">
                        <h4>法務防線警示</h4>
                        <ul>
                            <li>注意員工個資保護，現場糾紛中若顧客拍攝店員臉部並威脅公審，應由店長出面提醒不可散佈肖像。</li>
                            <li>提醒員工切勿在網路上使用私人帳號與顧客筆戰，避免火上加油。</li>
                        </ul>
                    </div>
                    <div class="legal-box training">
                        <h4>門市再培訓要點</h4>
                        <ul>
                            <li>帶位同仁必須學會「系統故障備援三部曲」口訣，並保持語氣溫和堅定。</li>
                            <li>尖峰時段加派一名店副理在門口進行情緒安撫與人流疏導。</li>
                        </ul>
                    </div>
                </div>
            `
        }
    },
    ptt: {
        command: "run-analysis --channel=ptt --topic=service-attitude --store=信義旗艦店",
        logs: [
            { tag: "[AGENT]", msg: "已追蹤 PTT 八卦版爆料貼文：'某某餐廳結帳員態度傲慢，丟零錢羞辱人。'", cls: "user-cmd" },
            { tag: "[AI ENGINE]", msg: "經核對收銀發票與結帳時間點 (14:32)... 確定該班別為兼職員工 A。該員最近兩週排班過長，有過勞跡象。", cls: "system-msg" },
            { tag: "[AI ENGINE]", msg: "社群反應：反感 (72%)。輿情擴散速率：低 (論壇發文 1 則/小時)。", cls: "warning-msg" },
            { tag: "[AI ENGINE]", msg: "商譽風險分數調升至 38 (Medium)。建議對該員實施關懷輔導並調離櫃檯。", cls: "warning-msg" },
            { tag: "[SYSTEM]", msg: "已生成 AI 決策支援模組 (原因解析/門市SOP/公關聲明/法務培訓)。", cls: "success-msg" }
        ],
        metrics: [91.0, 96.5, 4.70, 93.0, 38],
        outputs: {
            rootCause: `
                <div class="analysis-summary-block">
                    <span class="analysis-headline">PTT 態度爆料 - 原因追蹤</span>
                    <div class="analysis-points">
                        <div class="analysis-point-item"><strong>輿情源頭</strong> PTT 網友發文公審「結帳員臉臭、找零錢用丟的」，引發鄉民熱議「服務業態度差」。</div>
                        <div class="analysis-point-item"><strong>內部數據</strong> 當事員工 A 為工讀生，當週已排班 46 小時，且該時段經歷了連續 3 小時的收銀高峰，無替補休息。</div>
                        <div class="analysis-point-item"><strong>診斷結論</strong> 雖拋接零錢純屬疲憊手滑之誤會，但人員排班超時、櫃檯站點過久造成的生理與心理疲憊，是服務熱忱下降的根本原因。</div>
                    </div>
                </div>
            `,
            sop: `
                <ul class="sop-checklist">
                    <li class="sop-item"><input type="checkbox" id="p-sop-1"> <span>店經理約談該員工進行關懷，若有排班過重情況，立即調整排班時段，並調離收銀第一線。</span></li>
                    <li class="sop-item"><input type="checkbox" id="p-sop-2"> <span>增設「收銀限時輪值機制」，單人連續收銀時間不得超過 2 小時。</span></li>
                    <li class="sop-item"><input type="checkbox" id="p-sop-3"> <span>向發文顧客發送致歉私訊，解釋因疲憊手滑之誤會，並承諾改進人員調度。</span></li>
                </ul>
            `,
            pr: `
                <div class="pr-block" id="pr-statement-text-p">
您好，針對今日 PTT 論壇提及信義店結帳服務不佳的事件，本公司深感遺憾與抱歉。
經內部查核，當下因收銀尖峰時段同仁操作疲憊、找零時手滑造成您的誤解。我們已於第一時間對該位同仁進行關懷晤談，並檢討門市的排班工時與收銀輪替機制，避免人員過度疲勞影響服務品質。
我們將持續落實溫暖、尊重的服務規範，感謝您的回饋，讓我們有修正與改進的機會。
                </div>
                <div class="pr-actions">
                    <button class="btn btn-secondary btn-copy-pr" data-target="pr-statement-text-p">複製聲明</button>
                    <button class="btn btn-primary btn-publish-pr" data-type="PTT">回信致歉 PTT 網友</button>
                </div>
            `,
            legal: `
                <div class="legal-grid">
                    <div class="legal-box alert">
                        <h4>法務防線警示</h4>
                        <ul>
                            <li>注意勞基法工時上限，避免兼職同仁每週總工時超過規範，引發勞檢風險。</li>
                            <li>避免將員工個人姓名、照片流出至網路，保護員工隱私，避免引起內部反彈。</li>
                        </ul>
                    </div>
                    <div class="legal-box training">
                        <h4>門市再培訓要點</h4>
                        <ul>
                            <li>結帳「雙手找零與收付」標準動作再宣導，防止因快速投遞造成拋擲誤會。</li>
                            <li>店經理加強觀察現場同仁精神狀態，彈性調整後台休息時間。</li>
                        </ul>
                    </div>
                </div>
            `
        }
    }
};

function executeCrisisScenario(key) {
    const data = presetCrises[key];
    if (!data) return;
    
    // Clear active classes from trigger buttons
    document.querySelectorAll('.btn-primary-preset').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`trigger-crisis-${key}`).classList.add('active');
    
    // Terminal animation sequence
    terminal.innerHTML = '';
    printTerminalLog("[USER]", data.command, 'user-cmd');
    
    let delay = 0;
    data.logs.forEach((log, index) => {
        delay += 600;
        setTimeout(() => {
            printTerminalLog(log.tag, log.msg, log.cls);
            
            // Last step triggers output updates
            if (index === data.logs.length - 1) {
                // Populate tab contents
                document.getElementById('tab-root-cause').innerHTML = data.outputs.rootCause;
                document.getElementById('tab-sop').innerHTML = data.outputs.sop;
                document.getElementById('tab-pr').innerHTML = data.outputs.pr;
                document.getElementById('tab-legal').innerHTML = data.outputs.legal;
                
                // Show outputs panel
                decisionOutputs.style.display = 'block';
                
                // Set initial active tab
                switchTab('tab-root-cause');
                
                // Adjust dashboard metrics
                updateDashboardMetrics(data.metrics[0], data.metrics[1], data.metrics[2], data.metrics[3], data.metrics[4]);
                
                // Re-bind actions in generated tabs
                bindTabActions();
            }
        }, delay);
    });
}

function bindTabActions() {
    // Copy PR draft button
    document.querySelectorAll('.btn-copy-pr').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetId = e.target.getAttribute('data-target');
            const textEl = document.getElementById(targetId);
            if (textEl) {
                navigator.clipboard.writeText(textEl.textContent.trim())
                    .then(() => {
                        e.target.textContent = "已複製！";
                        setTimeout(() => { e.target.textContent = "複製聲明"; }, 2000);
                        printTerminalLog('[SYSTEM]', '公關聲明內容已成功複製至剪貼簿。', 'success-msg');
                    })
                    .catch(() => {
                        // Fallback
                        printTerminalLog('[SYSTEM]', '複製失敗，請手動複製。', 'warning-msg');
                    });
            }
        });
    });

    // Publish PR draft button
    document.querySelectorAll('.btn-publish-pr').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const channelType = e.target.getAttribute('data-type');
            e.target.disabled = true;
            e.target.textContent = "張貼中...";
            
            setTimeout(() => {
                e.target.textContent = "發布成功 ✓";
                printTerminalLog('[AI AGENT]', `公關應變聲明已成功串接發布至 ${channelType}。事件追蹤中。`, 'success-msg');
                
                // Recover metrics slightly
                const newRes = Math.min(100, metrics.resolutionRate + 4.0);
                const newRisk = Math.max(10, metrics.riskScore - 15);
                updateDashboardMetrics(metrics.brandScore, metrics.storeHealth, metrics.csat, newRes, newRisk);
            }, 1200);
        });
    });
    
    // Bind checklist monitoring to update resolution rate when user checks actions
    document.querySelectorAll('.sop-checklist input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', () => {
            const total = document.querySelectorAll('.sop-checklist input[type="checkbox"]').length;
            const checked = document.querySelectorAll('.sop-checklist input[type="checkbox"]:checked').length;
            
            printTerminalLog('[SYSTEM]', `SOP 執行進度更新：${checked}/${total}。`, 'system-msg');
            
            if (checked === total) {
                printTerminalLog('[AI AGENT]', '所有建議改善 SOP 已全數被執行與確認。品牌健康度開始回升。', 'success-msg');
                // Greatly reduce risk and improve score
                const newBrand = Math.min(100, metrics.brandScore + 3.0);
                const newRisk = Math.max(5, metrics.riskScore - 20);
                updateDashboardMetrics(newBrand, metrics.storeHealth, metrics.csat, 100.0, newRisk);
            }
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        }
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        if (content.id === tabId) {
            content.classList.add('active');
        }
    });
}

// Bind tabs switching events
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tabId = e.target.getAttribute('data-tab');
        switchTab(tabId);
    });
});

// Bind preset triggers
const triggerThreads = document.getElementById('trigger-crisis-threads');
const triggerGoogle = document.getElementById('trigger-crisis-google');
const triggerPtt = document.getElementById('trigger-crisis-ptt');

if (triggerThreads) triggerThreads.addEventListener('click', () => executeCrisisScenario('threads'));
if (triggerGoogle) triggerGoogle.addEventListener('click', () => executeCrisisScenario('google'));
if (triggerPtt) triggerPtt.addEventListener('click', () => executeCrisisScenario('ptt'));

// Sandbox custom parser rules
const btnSandboxAnalyze = document.getElementById('btn-sandbox-analyze');
const btnSandboxExample = document.getElementById('btn-sandbox-example');
const sandboxInput = document.getElementById('sandbox-input');
const sandboxLoading = document.getElementById('sandbox-loading');
const sandboxResults = document.getElementById('sandbox-results');

const sandboxExamples = [
    "信義店昨天服務極爛！我們等了一個多小時，點的招牌牛肉送上來居然還是冰的，反應了店員還擺臭臉，叫主管來才不情不願道歉，這種店吃一次就夠了！",
    "忠孝SOGO店的服務生Apple態度超好，很有耐心解說菜單，做完的美甲花色很美，非常細緻。一定會再回訪的，大推！",
    "路過台中店覺得裝潢很好看就進去了，等候時間還好大概十分鐘，只是餐點味道很普通，以這個價位來說算貴的，沒有評論上寫得那麼神。"
];

if (btnSandboxExample) {
    btnSandboxExample.addEventListener('click', () => {
        const index = Math.floor(Math.random() * sandboxExamples.length);
        sandboxInput.value = sandboxExamples[index];
    });
}

if (btnSandboxAnalyze) {
    btnSandboxAnalyze.addEventListener('click', () => {
        const text = sandboxInput.value.trim();
        if (!text) {
            alert('請輸入一些評論文字再執行分析！');
            return;
        }
        
        // Hide previous results and show scanner loading
        sandboxResults.style.display = 'none';
        sandboxLoading.style.display = 'flex';
        
        // Dynamic NLP parsing simulation
        setTimeout(() => {
            sandboxLoading.style.display = 'none';
            
            // Simple keyword rules to make the sandbox interactive and realistic
            let sentiment = "Positive (92%)";
            let sentimentClass = "positive";
            let emotion = "Joy 😊 / Satisfaction 👍";
            let touchpoint = "Service (服務體驗) & Product (餐點品質)";
            let risk = "Low Risk (5)";
            let riskClass = "low";
            let pr = "您好，感謝您對我們服務與品質的肯定！我們會持續維持高品質水準，期待下次再度為您提供愉快的體驗。";
            let ops = [
                "維持當前服務規範，將該店同仁的優秀事蹟記錄入本月考核指標。",
                "持續維持食材供應鏈的穩定品質。"
            ];
            
            const lowerText = text.toLowerCase();
            if (lowerText.includes('爛') || lowerText.includes('冰') || lowerText.includes('臭臉') || lowerText.includes('生氣') || lowerText.includes('等很久') || lowerText.includes('拉肚子') || lowerText.includes('肚子痛') || lowerText.includes('差')) {
                sentiment = "Negative (96%)";
                sentimentClass = "negative";
                emotion = "Anger 😠 / Frustration 😩";
                
                if (lowerText.includes('等') || lowerText.includes('候')) {
                    touchpoint = "Wait (等候到店) & Service (服務體驗)";
                } else if (lowerText.includes('冰') || lowerText.includes('不新鮮') || lowerText.includes('拉肚子')) {
                    touchpoint = "Service (服務體驗) & Product (食品品質)";
                } else {
                    touchpoint = "Service (服務體驗) / Touchpoint friction";
                }
                
                if (lowerText.includes('拉肚子') || lowerText.includes('毒') || lowerText.includes('集體')) {
                    risk = "CRITICAL Risk (85)";
                    riskClass = "high";
                    pr = "您好，非常抱歉讓您遭遇此用餐情況。本公司高度重視此食安疑慮，已立刻責成相關分店主管清查冷鏈儲存與廚房作業。我們非常關切您的身體狀況，請您方便撥冗聯絡我們，以便安排就醫複查與全額補償。";
                    ops = [
                        "分店立即對冷鏈及食材新鮮度進行自主封存與送驗。",
                        "對當日收發貨及庫存食材清單進行回溯排查。"
                    ];
                } else {
                    risk = "High Risk (72)";
                    riskClass = "high";
                    pr = "您好，十分抱歉讓您在此次用餐中感到不愉快。針對您提及的餐點溫度及員工態度問題，我們已立即轉達分店店長進行整頓與加強教育訓練，並將嚴格監督出餐覆核。希望您給予我們改進的機會。";
                    ops = [
                        "要求分店落實出餐雙重核對，並於現場進行人員應對培訓督導。",
                        "店經理親自向顧客致電說明改善計畫並致歉。"
                    ];
                }
            } else if (lowerText.includes('普通') || lowerText.includes('還好') || lowerText.includes('一般') || lowerText.includes('貴')) {
                sentiment = "Neutral (60%)";
                sentimentClass = "neutral";
                emotion = "Neutral 😐 / Evaluation 🤔";
                touchpoint = "Product (餐點品質) & Price (價格認知)";
                risk = "Low Risk (15)";
                riskClass = "low";
                pr = "您好，感謝您的回饋。我們會持續聽取各方顧客意見，對產品的性價比與口味進行優化。期待未來能為您提供更為驚艷的服務。";
                ops = [
                    "記錄顧客對於價格與餐點美味度的性價比回饋，彙整給研發總部。",
                    "定期觀察對手品牌同價位產品的競爭力。"
                ];
            }
            
            // Inject results into UI
            const sentEl = document.getElementById('sandbox-sentiment');
            sentEl.textContent = sentiment;
            sentEl.className = `result-val sentiment-badge ${sentimentClass}`;
            
            document.getElementById('sandbox-emotion').textContent = emotion;
            document.getElementById('sandbox-touchpoint').textContent = touchpoint;
            
            const riskEl = document.getElementById('sandbox-risk');
            riskEl.textContent = risk;
            riskEl.className = `result-val risk-text ${riskClass}`;
            
            document.getElementById('sandbox-pr-rec').textContent = pr;
            
            const opsList = document.getElementById('sandbox-ops-rec');
            opsList.innerHTML = ops.map(item => `<li>${item}</li>`).join('');
            
            // Show results block
            sandboxResults.style.display = 'block';
            
            // Dynamically affect overall risk based on sandbox testing
            if (riskClass === 'high') {
                const newBrand = Math.max(80, metrics.brandScore - 1.0);
                const newRisk = Math.min(100, metrics.riskScore + 8);
                updateDashboardMetrics(newBrand, metrics.storeHealth, metrics.csat, metrics.resolutionRate, newRisk);
            }
            
        }, 1500);
    });
}

// Start Simulated Streaming on load
window.addEventListener('DOMContentLoaded', () => {
    initStream();
});
