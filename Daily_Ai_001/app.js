document.addEventListener('DOMContentLoaded', () => {
    // State management
    const state = {
        currentGasCar: 'RAV4',
        annualMileage: 15000,
        drivingStyle: 'balanced',
        selectedRoute: 'commute',
        detectedPersona: '未識別',
        savings: 0,
        useBackend: false // Will be set to true if backend is active
    };

    // DOM Elements
    const gasCarSelect = document.getElementById('gas-car');
    const mileageSlider = document.getElementById('mileage');
    const mileageVal = document.getElementById('mileage-val');
    const styleSelect = document.getElementById('driving-style');
    
    const tcoAmount = document.getElementById('tco-amount');
    const gasBar = document.getElementById('gas-bar');
    const evBar = document.getElementById('ev-bar');
    const gasVal = document.getElementById('gas-val');
    const evVal = document.getElementById('ev-val');

    const routeBtns = document.querySelectorAll('.route-btn');
    const progressLine = document.getElementById('progress-line');
    const timelinePoints = document.querySelectorAll('.timeline-point');
    const simDistance = document.getElementById('sim-distance');
    const simSoc = document.getElementById('sim-soc');
    const simTime = document.getElementById('sim-time');
    const simChargers = document.getElementById('sim-chargers');

    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const presetBtns = document.querySelectorAll('.preset-btn');
    const personaBadge = document.getElementById('persona-badge');

    const bookBtn = document.getElementById('book-btn');
    const ticketModal = document.getElementById('ticket-modal');
    const closeTicket = document.getElementById('close-ticket');
    const qrImage = document.getElementById('qr-image');
    const ticketPersona = document.getElementById('ticket-persona');
    const ticketSavings = document.getElementById('ticket-savings');
    const ticketRoute = document.getElementById('ticket-route');

    const BACKEND_URL = 'http://127.0.0.1:8000';

    // Check if FastAPI Backend is active
    async function checkBackendStatus() {
        try {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 1000); // 1s timeout
            const res = await fetch(BACKEND_URL, { signal: controller.signal });
            clearTimeout(id);
            if (res.ok) {
                state.useBackend = true;
                console.log("▲ TOYOTA EV LifePilot: FastAPI Backend Detected! Operating in Client-Server Mode.");
                document.querySelector('.badge-live').innerText = "CLIENT-SERVER CONNECTED";
                document.querySelector('.badge-live').style.background = "rgba(59, 130, 246, 0.15)";
                document.querySelector('.badge-live').style.color = "var(--color-primary)";
                document.querySelector('.badge-live').style.borderColor = "rgba(59, 130, 246, 0.3)";
            }
        } catch (e) {
            console.log("▲ TOYOTA EV LifePilot: Backend offline. Operating in Standalone Mock Mode.");
        }
        // Run initial calculations after status is checked
        updateTCO();
        runSimulation('commute');
    }

    // 1. TCO Calculator Logic
    const carDatabase = {
        RAV4: { fuelEff: 13.7, maint5Yr: 95000, tax5Yr: 112000 },
        Altis: { fuelEff: 15.6, maint5Yr: 75000, tax5Yr: 60000 },
        Camry: { fuelEff: 12.5, maint5Yr: 110000, tax5Yr: 112000 }
    };

    const bZ4X = {
        efficiency: 6.2, 
        maint5Yr: 35000,  
        tax5Yr: 0
    };

    const FUEL_PRICE = 31.5; 
    const ELEC_PRICE = 6.5;   

    async function updateTCO() {
        if (state.useBackend) {
            try {
                const res = await fetch(`${BACKEND_URL}/api/predict-tco`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        gas_car: state.currentGasCar,
                        annual_mileage: state.annualMileage,
                        driving_style: state.drivingStyle
                    })
                });
                const data = await res.json();
                
                state.savings = data.savings;
                tcoAmount.innerText = `NT$ ${Math.round(data.savings).toLocaleString()}`;
                
                const maxCost = Math.max(data.gas_cost, data.ev_cost);
                const gasPercent = (data.gas_cost / maxCost) * 100;
                const evPercent = (data.ev_cost / maxCost) * 100;

                gasBar.style.width = `${gasPercent}%`;
                evBar.style.width = `${evPercent}%`;

                gasVal.innerText = `NT$ ${Math.round(data.gas_cost).toLocaleString()}`;
                evVal.innerText = `NT$ ${Math.round(data.ev_cost).toLocaleString()}`;
                return;
            } catch (e) {
                console.error("Backend TCO error, falling back to local:", e);
            }
        }

        // Local Fallback
        const gasCar = carDatabase[state.currentGasCar];
        const mileage = state.annualMileage;
        const styleFactor = state.drivingStyle === 'sporty' ? 1.15 : (state.drivingStyle === 'eco' ? 0.9 : 1.0);

        const totalLiters = (mileage * 5) / (gasCar.fuelEff / styleFactor);
        const fuelCost5Yr = totalLiters * FUEL_PRICE;
        const totalGasCost = fuelCost5Yr + gasCar.maint5Yr + gasCar.tax5Yr;

        const totalKwh = (mileage * 5) / (bZ4X.efficiency * styleFactor);
        const electricityCost5Yr = totalKwh * ELEC_PRICE;
        const totalEvCost = electricityCost5Yr + bZ4X.maint5Yr + bZ4X.tax5Yr;

        const 5YrSavings = totalGasCost - totalEvCost;
        state.savings = 5YrSavings;

        tcoAmount.innerText = `NT$ ${Math.round(5YrSavings).toLocaleString()}`;
        
        const maxCost = Math.max(totalGasCost, totalEvCost);
        const gasPercent = (totalGasCost / maxCost) * 100;
        const evPercent = (totalEvCost / maxCost) * 100;

        gasBar.style.width = `${gasPercent}%`;
        evBar.style.width = `${evPercent}%`;

        gasVal.innerText = `NT$ ${Math.round(totalGasCost).toLocaleString()}`;
        evVal.innerText = `NT$ ${Math.round(totalEvCost).toLocaleString()}`;
    }

    // Event Listeners for TCO Inputs
    gasCarSelect.addEventListener('change', (e) => {
        state.currentGasCar = e.target.value;
        updateTCO();
    });

    mileageSlider.addEventListener('input', (e) => {
        state.annualMileage = parseInt(e.target.value);
        mileageVal.innerText = `${state.annualMileage.toLocaleString()} 公里`;
        updateTCO();
    });

    styleSelect.addEventListener('change', (e) => {
        state.drivingStyle = e.target.value;
        updateTCO();
    });

    // 2. Route & SoC Simulator Logic
    const localRoutes = {
        commute: {
            distance: '82 公里',
            time: '1 小時 15 分',
            chargers: '極致省心！無需中途充電',
            timeline: [
                { name: '台北出發', soc: 100 },
                { name: '國道三號 (巡航)', soc: 89 },
                { name: '新竹科學園區 (抵達)', soc: 78 }
            ]
        },
        mountain: {
            distance: '54 公里',
            time: '1 小時 5 分',
            chargers: '越開電越多！動能回充啟動',
            timeline: [
                { name: '台北出發', soc: 100 },
                { name: '坪林山頂 (爬坡)', soc: 82 }, 
                { name: '礁溪抵達 (下坡回充)', soc: 86 }
            ]
        },
        longdistance: {
            distance: '318 公里',
            time: '3 小時 40 分',
            chargers: '清水服務區 U-POWER 補電 15 分鐘',
            timeline: [
                { name: '台北出發', soc: 100 },
                { name: '清水服務區 (超充)', soc: 35 }, 
                { name: '台南花園夜市 (抵達)', soc: 80 }  
            ]
        }
    };

    async function runSimulation(routeId) {
        state.selectedRoute = routeId;
        let routeData = localRoutes[routeId];

        if (state.useBackend) {
            try {
                const res = await fetch(`${BACKEND_URL}/api/simulate-route?route_id=${routeId}`, { method: 'POST' });
                routeData = await res.json();
            } catch (e) {
                console.error("Backend simulation error, falling back:", e);
            }
        }

        // Reset Timeline UI
        progressLine.style.width = '0%';
        timelinePoints.forEach(p => p.classList.remove('active'));

        // Update Text Stats
        simDistance.innerText = routeData.distance;
        simTime.innerText = routeData.time;
        simChargers.innerText = routeData.chargers;
        
        // Trigger animation
        setTimeout(() => {
            progressLine.style.width = '100%';
            
            // Animate points one by one
            routeData.timeline.forEach((point, idx) => {
                setTimeout(() => {
                    const pointElem = timelinePoints[idx];
                    if (pointElem) {
                        pointElem.classList.add('active');
                        pointElem.querySelector('.point-label').innerText = point.name;
                        pointElem.querySelector('.point-soc').innerText = `${point.soc}%`;
                        
                        if (idx === routeData.timeline.length - 1) {
                            simSoc.innerText = `${point.soc}%`;
                        }
                    }
                }, idx * 500);
            });
        }, 100);
    }

    routeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            routeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            runSimulation(btn.dataset.route);
        });
    });

    // 3. Empathetic Chatbot Demo
    const localChatbotDatabase = {
        dad: {
            persona: '守護家人的滿分爸爸 👨‍👩‍👦',
            userMsg: '我很在乎老婆和小孩坐車的感受，如果載全家人去中南部或宜蘭玩，充電會不會很不方便？會讓小孩等很久嗎？',
            botMsg: '爸爸您好！非常理解您的顧慮，載著全家人出遊，最怕的就是小孩在車上哭鬧或者排隊充電耽誤行程。其實，這台 bZ4X 就是為守護家庭而生的「移動靜音城堡」！`n`n**1. 塞車不再是噩夢**：`n`n以前開油車在雪隧或國道塞車，引擎怠速抖動、廢氣味重，還要看著油錢一直燒。換了 bZ4X，塞車時車內是安靜如圖書館的無震動空間，空調持續釋放過濾過的清新空氣，不浪費一滴油，老婆和小孩能在後座安穩熟睡，這才是真正的豪華享受。`n`n**2. 充電比換尿布還快**：`n`n我們特別與全台最頂級的 **U-POWER 快速充電網** 深度整合。以您常帶家人去的宜蘭為例，bZ4X 的超高速快充只需 **15 到 20 分鐘**（剛好是全家下車上個廁所、幫小孩換個尿布、買杯咖啡的時間），電量就從 10% 補足到 80% 了！您根本不需要「專程等待充電」，而是讓充電完美融合在全家人的休息節奏中。買下它，帶給家人更舒適、更有質感的旅行回憶！'
        },
        tech: {
            persona: '追求極致的科技先鋒 🚀',
            userMsg: '我想體驗純電的熱血科技，但現在電車的電池技術迭代很快，我很擔心過幾年電池衰退或者保固的問題。買這台真的有保障嗎？',
            botMsg: '科技迷的眼光非常精準！這也是許多喜愛高科技的車主最核心的考量。但我要告訴您：**「選擇電動車，TOYOTA 廠徽就是您最強大的保值與安全雙重保證！」**`n`n**1. 凌駕於新創品牌的保值神話**：`n`n在台灣，TOYOTA 代表的就是「保值神話」與「最安心的售後後勤」。許多新創電車品牌幾年後折舊慘烈、維修無門。而 bZ4X 掛著 TOYOTA 的招牌，就是未來二手市場的黃金保證。全台最密集的原廠服務廠，隨時是您的後盾。`n`n**2. 25年零事故的電池安全科技**：`n`nTOYOTA 發展電動化技術超過 25 年，締造了「全球電池零重大安全事故」的傲人紀錄。我們對 bZ4X 的電池極具信心，直接提供 **「8 年或 16 萬公里」超長原廠保固**（保證容量 70% 以上）。搭配先進的智慧液冷溫控系統，即使在台灣炎熱的夏季高速奔馳，電池依然維持在最完美的運作溫度。這是一台讓您既能享受純電瞬間扭力的激情，又完全無需為未來擔憂的科技傑作！'
        },
        commuter: {
            persona: '精打細算的購車贏家 📈',
            userMsg: '我每天都要開車通勤，到底換這台 bZ4X 划不划算？油轉電之後保養和稅金能幫我省下多少錢？',
            botMsg: '您問到了最核心、也最讓人興奮的關鍵！讓我們用最實在的數據說話，您看完一定會想立刻下單！`n`n以您設定的年行駛 **${mileage} 公里** 來算：`n`n**1. 電費直接打對折再對折**：`n`n現在中油 95 無鉛汽油每公升突破 31 元，開油車通勤每天都在燒錢。而 bZ4X 一度電可以跑 6.2 公里，如果您善用離峰時間充電，**每公里的電費不到 1 元**！`n`n**2. 保養與稅金幾乎歸零**：`n`n電動車沒有引擎、變速箱、油路與複雜耗材，5 年保養費用直接從燃油車的近 10 萬元，暴降到只剩 3.5 萬元！再加上台灣目前純電車免徵牌照稅與燃料費。`n`n**3. 5年幫您多賺一趟歐洲雙人遊**：`n`n**5 年下來，這台車直接幫您省下高達 NT$ ${savings} 的真金白銀！** 這筆錢相當於免費送您和家人一趟歐洲雙人遊，或是好幾年的家庭生活基金。開著一輛配備滿載、安靜舒適的百萬級純電 SUV 通勤，同時還能為自己省下大筆財富，這才是最聰明的消費決定！'
        }
    };

    function appendMessage(sender, text, isHtml = false) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        
        if (isHtml) {
            msgDiv.innerHTML = text.replace(/`n/g, '<br>');
        } else {
            msgDiv.innerText = text;
        }
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function triggerPersonaChat(personaKey) {
        const localData = localChatbotDatabase[personaKey];
        appendMessage('user', localData.userMsg);

        if (state.useBackend) {
            try {
                const res = await fetch(`${BACKEND_URL}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: localData.userMsg,
                        current_persona: state.detectedPersona
                    })
                });
                const data = await res.json();
                
                state.detectedPersona = data.detected_persona;
                personaBadge.innerText = `AI 購車領航員 (當前識別：${data.detected_persona})`;
                personaBadge.style.background = 'var(--color-secondary)';
                
                setTimeout(() => {
                    appendMessage('bot', data.reply, true);
                    console.log("RAG Retrieved Docs:", data.retrieved_documents);
                }, 800);
                return;
            } catch (e) {
                console.error("Backend chat error, falling back:", e);
            }
        }

        // Local Fallback
        state.detectedPersona = localData.persona;
        personaBadge.innerText = `AI 購車領航員 (當前識別：${localData.persona})`;
        personaBadge.style.background = 'var(--color-secondary)';

        setTimeout(() => {
            let reply = localData.botMsg;
            if (personaKey === 'commuter') {
                reply = reply.replace('${mileage}', state.annualMileage.toLocaleString())
                             .replace('${savings}', Math.round(state.savings).toLocaleString());
            }
            appendMessage('bot', reply, true);
        }, 800);
    }

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            triggerPersonaChat(btn.dataset.persona);
        });
    });

    sendBtn.addEventListener('click', async () => {
        const txt = chatInput.value.trim();
        if (!txt) return;

        appendMessage('user', txt);
        chatInput.value = '';

        if (state.useBackend) {
            try {
                const res = await fetch(`${BACKEND_URL}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: txt,
                        current_persona: state.detectedPersona
                    })
                });
                const data = await res.json();
                state.detectedPersona = data.detected_persona;
                personaBadge.innerText = `AI 購車領航員 (當前識別：${data.detected_persona})`;
                personaBadge.style.background = 'var(--color-secondary)';
                
                setTimeout(() => {
                    appendMessage('bot', data.reply, true);
                }, 800);
                return;
            } catch (e) {
                console.error("Backend custom chat error:", e);
            }
        }

        setTimeout(() => {
            appendMessage('bot', '收到您的提問！我是您的 AI 領航員。建議您可以直接點選下方的「快速提問」按鈕，體驗我針對台灣車主日常情境（家庭出遊、科技保值、通勤精算）為您量身打造的共情解說，絕對會讓您對 TOYOTA bZ4X 充滿期待！', true);
        }, 800);
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendBtn.click();
    });

    // 4. O2O Ticket Generation & Modal
    bookBtn.addEventListener('click', async () => {
        const currentPersonaName = state.detectedPersona === '未識別' ? '熱血準車主' : state.detectedPersona;
        let routeName = '台北 ➔ 新竹科學園區 (零焦慮通勤體驗)';
        if (state.selectedRoute === 'mountain') routeName = '台北 ➔ 宜蘭礁溪 (雪隧靜音與山路回充體驗)';
        else if (state.selectedRoute === 'longdistance') routeName = '台北 ➔ 台南 (清水服務區超充對接體驗)';

        ticketPersona.innerText = currentPersonaName;
        ticketSavings.innerText = `NT$ ${Math.round(state.savings).toLocaleString()}`;
        ticketRoute.innerText = routeName;

        if (state.useBackend) {
            try {
                const res = await fetch(`${BACKEND_URL}/api/generate-pass`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        persona: currentPersonaName,
                        savings: state.savings,
                        route: routeName
                    })
                });
                const data = await res.json();
                qrImage.src = data.qr_url;
                ticketModal.classList.add('open');
                return;
            } catch (e) {
                console.error("Backend ticket error, falling back:", e);
            }
        }

        // Local Fallback
        const qrData = encodeURIComponent(`TOYOTA_EV_PASS|Persona:${currentPersonaName}|Savings:${state.savings}|Route:${state.selectedRoute}`);
        qrImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${qrData}`;
        ticketModal.classList.add('open');
    });

    closeTicket.addEventListener('click', () => {
        ticketModal.classList.remove('open');
    });

    ticketModal.addEventListener('click', (e) => {
        if (e.target === ticketModal) {
            ticketModal.classList.remove('open');
        }
    });

    // Run Backend Status Check (will trigger TCO & Simulation init internally)
    checkBackendStatus();
    
    // Welcome message from bot
    setTimeout(() => {
        appendMessage('bot', '您好！歡迎來到 **TOYOTA EV LifePilot**。我是您的專屬 AI 購車領航員。`n`n這是一場關於「科技、安靜與極致省錢」的全新生活提案。請在左側選擇您目前的燃油車款與年里程，我會即時為您精算出**「油轉電」令人心動的省錢實感**；同時，您可以在下方點選您的用車情境，讓我為您規劃零里程焦慮的台灣一日生活，並解答您對電車的所有疑慮。讓我們一起開啟智慧純電生活！', true);
    }, 500);
});
