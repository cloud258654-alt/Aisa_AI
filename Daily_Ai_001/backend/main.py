from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import urllib.parse

app = FastAPI(
    title="TOYOTA EV LifePilot Backend API",
    description="和泰 2026 AI 黑客松 - 油轉電智慧領航員後端服務",
    version="1.0.0"
)

# Enable CORS so our frontend index.html (running on double-click or local server) can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class TcoRequest(BaseModel):
    gas_car: str
    annual_mileage: int
    driving_style: str

class TcoResponse(BaseModel):
    savings: float
    gas_cost: float
    ev_cost: float
    message: str

class RouteTimelinePoint(BaseModel):
    name: str
    soc: int

class RouteSimulationResponse(BaseModel):
    route_id: str
    distance: str
    time: str
    chargers: str
    timeline: List[RouteTimelinePoint]

class ChatRequest(BaseModel):
    message: str
    current_persona: Optional[str] = "未識別"

class ChatResponse(BaseModel):
    reply: str
    detected_persona: str
    retrieved_documents: List[str]

class PassRequest(BaseModel):
    persona: str
    savings: float
    route: str

class PassResponse(BaseModel):
    qr_url: str
    ticket_id: str
    status: str

# --- TCO Calculation Databases (ML Placeholder) ---
CAR_DATABASE = {
    "RAV4": {"fuel_eff": 13.7, "maint_5yr": 95000, "tax_5yr": 112000},
    "Altis": {"fuel_eff": 15.6, "maint_5yr": 75000, "tax_5yr": 60000},
    "Camry": {"fuel_eff": 12.5, "maint_5yr": 110000, "tax_5yr": 112000}
}

BZ4X_CONFIG = {
    "efficiency": 6.2, # km/kWh
    "maint_5yr": 35000,
    "tax_5yr": 0
}

FUEL_PRICE = 31.5
ELEC_PRICE = 6.5

# --- RAG Mock Knowledge Base ---
MOCK_KNOWLEDGE_BASE = {
    "battery_safety": [
        "TOYOTA bZ4X 採用專屬 e-TNGA 平台，電池模組配置於車底，具備碰撞保護鋼樑保護結構。",
        "TOYOTA 具備 25 年電能化車款（含 Prius Hybrid）研發經驗，保持全球銷售零電池安全事故紀錄。",
        "bZ4X 提供電池 8 年或 16 萬公里（容量 70% 以上）原廠保固，並由和泰全台最密集服務廠後勤支援。"
    ],
    "charging_speed": [
        "bZ4X 支援最高 150kW DC 快充，配合 U-POWER 超高速充電，10% 充至 80% 僅需約 30 分鐘。",
        "配合台灣日常通勤與休閒情境，如雪山隧道塞車或坪林山路，下坡路段可啟動動能回充（Regenerative Braking）增加續航力。"
    ],
    "economics": [
        "純電動車免徵牌照稅與燃料費。無引擎、油路、變速箱耗材，5年保養費用較燃油車省下近65%。",
        "以台灣平均電價與油價換算，電動車每公里電費成本低於 1 元，相較燃油車省下超過 60% 油資。"
    ]
}

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "running", "service": "TOYOTA EV LifePilot API", "version": "1.0.0"}

@app.post("/api/predict-tco", response_model=TcoResponse)
def predict_tco(request: TcoRequest):
    if request.gas_car not in CAR_DATABASE:
        raise HTTPException(status_code=400, detail="未支援的比較車款")
    
    gas_car = CAR_DATABASE[request.gas_car]
    mileage = request.annual_mileage
    
    # Driving style factor adjustment (simulating feature engineering)
    style_factor = 1.15 if request.driving_style == "sporty" else (0.9 if request.driving_style == "eco" else 1.0)
    
    # Calculate 5-year gas cost
    total_liters = (mileage * 5) / (gas_car["fuel_eff"] / style_factor)
    fuel_cost = total_liters * FUEL_PRICE
    total_gas_cost = fuel_cost + gas_car["maint_5yr"] + gas_car["tax_5yr"]
    
    # Calculate 5-year bZ4X cost
    total_kwh = (mileage * 5) / (BZ4X_CONFIG["efficiency"] * style_factor)
    elec_cost = total_kwh * ELEC_PRICE
    total_ev_cost = elec_cost + BZ4X_CONFIG["maint_5yr"] + BZ4X_CONFIG["tax_5yr"]
    
    savings = total_gas_cost - total_ev_cost
    
    # Evocative summary message
    message = (
        f"換購 bZ4X 後，您每年平均可省下約 {round(savings/5):,} 元用車花費！"
        f"5 年累計賺回 {round(savings):,} 元，直接為您全家省下一趟歐洲雙人遊基金！"
    )
    
    return TcoResponse(
        savings=savings,
        gas_cost=total_gas_cost,
        ev_cost=total_ev_cost,
        message=message
    )

@app.post("/api/simulate-route", response_model=RouteSimulationResponse)
def simulate_route(route_id: str):
    routes = {
        "commute": RouteSimulationResponse(
            route_id="commute",
            distance="82 公里",
            time="1 小時 15 分",
            chargers="極致省心！無需中途充電",
            timeline=[
                RouteTimelinePoint(name="台北出發", soc=100),
                RouteTimelinePoint(name="國道三號 (巡航)", soc=89),
                RouteTimelinePoint(name="新竹科學園區 (抵達)", soc=78)
            ]
        ),
        "mountain": RouteSimulationResponse(
            route_id="mountain",
            distance="54 公里",
            time="1 小時 5 分",
            chargers="越開電越多！下坡動能回充啟動",
            timeline=[
                RouteTimelinePoint(name="台北出發", soc=100),
                RouteTimelinePoint(name="坪林山頂 (爬坡)", soc=82),
                RouteTimelinePoint(name="礁溪抵達 (下坡回充)", soc=86)
            ]
        ),
        "longdistance": RouteSimulationResponse(
            route_id="longdistance",
            distance="318 公里",
            time="3 小時 40 分",
            chargers="清水服務區 U-POWER 補電 15 分鐘",
            timeline=[
                RouteTimelinePoint(name="台北出發", soc=100),
                RouteTimelinePoint(name="清水服務區 (超充)", soc=35),
                RouteTimelinePoint(name="台南花園夜市 (抵達)", soc=80)
            ]
        )
    }
    
    if route_id not in routes:
        raise HTTPException(status_code=404, detail="找不到指定路線")
        
    return routes[route_id]

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    msg = request.message.lower()
    detected_persona = request.current_persona
    retrieved_docs = []
    reply = ""
    
    # 1. Mock RAG retrieval logic & Persona Detection
    if "充電" in msg or "出遠門" in msg or "塞車" in msg or "小孩" in msg:
        detected_persona = "守護家人的滿分爸爸 👨‍👩‍👦"
        retrieved_docs = MOCK_KNOWLEDGE_BASE["charging_speed"]
        reply = (
            "非常理解您的顧慮！帶著家人出遊，最怕的就是小孩在車上哭鬧或者排隊充電耽誤行程。`n`n"
            "**TOYOTA bZ4X 就是您守護家庭的「移動靜音城堡」！**`n`n"
            "當您在雪隧或國道塞車時，車內完全安靜、無引擎怠速震動，空調能持續過濾並提供清新空氣，不浪費任何汽油。`n`n"
            "而在充電上，配合全台最頂級的 **U-POWER 快速充電網**，bZ4X 的超高速快充只需 **15-20分鐘**（剛好是全家下車上個廁所、買杯咖啡的時間），電量就能從 10% 補足到 80%。"
            "充電完全能融入您的休息節奏，給家人更有質感的旅行回憶！"
        )
    elif "電池" in msg or "保固" in msg or "衰退" in msg or "保值" in msg:
        detected_persona = "追求極致的科技先鋒 🚀"
        retrieved_docs = MOCK_KNOWLEDGE_BASE["battery_safety"]
        reply = (
            "您的考量非常專業！這也是喜愛科技的車主最核心的關注點。但請記住：**「在台灣，選擇電動車，TOYOTA 廠徽就是您高保值與售後後勤的最強保證！」**`n`n"
            "相較於許多折舊率高、維修無門的新創電車品牌，bZ4X 掛著 TOYOTA 這塊台灣汽車市場的「保值黃金招牌」，代表極高的二手殘值。`n`n"
            "此外，TOYOTA 擁有 25 年電能化技術經驗，創造了全球零電池重大安全事故紀錄。原廠提供高規格的 **「8 年或 16 萬公里」電池保固**，搭配先進的液冷溫控系統，"
            "讓您安心享受純電操駕的瞬間快感，完全免除後顧之憂！"
        )
    elif "划不划算" in msg or "通勤" in msg or "省錢" in msg or "保養" in msg or "稅金" in msg:
        detected_persona = "精打細算的購車贏家 📈"
        retrieved_docs = MOCK_KNOWLEDGE_BASE["economics"]
        reply = (
            "您問到了最實在也最聰明的痛點！油轉電後的經濟回報絕對會讓您想要立刻下單！`n`n"
            "**1. 電費極低**：bZ4X 每公里電費不到 1 元，相較於高昂的 95/98 汽油，電費直接幫您打對折再對折！`n`n"
            "**2. 保養免除**：電車沒有引擎、油路與複雜耗材，5 年定保成本從油車的 10 萬元暴降至約 3.5 萬元！`n`n"
            "**3. 稅金減免**：目前台灣對純電車免徵牌照稅與燃料費。綜合下來，5 年為您省下的數十萬元，**相當於直接幫您和伴侶賺回一趟歐洲豪華雙人遊**！"
            "開著高質感的百萬純電 SUV 通勤，同時還能為自己省下大筆財富，這才是最智慧的用車決定！"
        )
    else:
        # Default response
        retrieved_docs = MOCK_KNOWLEDGE_BASE["economics"] + MOCK_KNOWLEDGE_BASE["battery_safety"]
        reply = (
            "歡迎詢問！TOYOTA bZ4X 結合了前所未有的「靜音舒適」、「超低持有成本（5年可省數十萬）」與「8年16萬公里安心電池保固」。"
            "您可以直接點選下方的「快速提問」按鈕，體驗我針對家庭出遊、保值安全與通勤省錢為您量身打造的共情解說！"
        )
        
    return ChatResponse(
        reply=reply,
        detected_persona=detected_persona,
        retrieved_documents=retrieved_docs
    )

@app.post("/api/generate-pass", response_model=PassResponse)
def generate_pass(request: PassRequest):
    ticket_id = f"TYT-EV-{hash(request.persona) % 100000:05d}"
    
    # Encode values for QR Code
    qr_data = f"TOYOTA_EV_PASS|ID:{ticket_id}|Persona:{request.persona}|Savings:{request.savings}|Route:{request.route}"
    encoded_data = urllib.parse.quote(qr_data)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={encoded_data}"
    
    return PassResponse(
        qr_url=qr_url,
        ticket_id=ticket_id,
        status="active"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
