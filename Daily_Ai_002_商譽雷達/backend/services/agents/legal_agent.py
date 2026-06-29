from datetime import datetime
from typing import Any, Dict, List, Optional
from .base import BaseAgent


COMPLIANCE_CHECKLIST = {
    "food_safety": [
        "食品安全衛生管理法 - 食品良好衛生規範準則(GHP)",
        "食品安全衛生管理法 - 食品業者登錄制度",
        "食品安全衛生管理法 - 產品標示規定",
        "食品安全衛生管理法 - 食品召回制度",
        "食品及其相關產品追溯追蹤系統管理辦法",
        "食品業者投保產品責任保險規定",
    ],
    "hygiene": [
        "食品安全衛生管理法 - 食品良好衛生規範準則(GHP)",
        "廢棄物清理法 - 事業廢棄物處理規定",
        "建築法 - 公共安全檢查",
        "消防法 - 消防安全設備檢修申報",
        "傳染病防治法 - 營業場所衛生管理",
    ],
    "data_privacy": [
        "個人資料保護法 - 告知義務與同意",
        "個人資料保護法 - 資料安全維護措施",
        "個人資料保護法 - 當事人權利行使",
        "個人資料保護法 - 事故通報機制",
        "歐盟GDPR(如涉及跨國客戶資料)",
    ],
    "labor": [
        "勞動基準法 - 工時與加班規定",
        "勞動基準法 - 一例一休與休假規定",
        "勞動基準法 - 工資給付原則",
        "勞工保險條例 - 投保規定",
        "職業安全衛生法 - 工作環境安全",
        "性別工作平等法 - 職場性騷擾防治",
    ],
    "consumer_protection": [
        "消費者保護法 - 定型化契約條款",
        "消費者保護法 - 廣告真實義務",
        "消費者保護法 - 消費爭議處理",
        "消費者保護法 - 懲罰性賠償金",
        "公平交易法 - 不實廣告禁止",
    ],
    "defamation": [
        "刑法第310條 - 誹謗罪構成要件",
        "刑法第311條 - 善意發表言論免責",
        "刑法第313條 - 妨害信用罪",
        "民法第195條 - 名譽權侵害賠償",
        "公平交易法第24條 - 營業信譽保護",
    ],
}

REGULATORY_REQUIREMENTS = {
    "food_safety": {
        "reporting_authority": "地方衛生局 / 食品藥物管理署(TFDA)",
        "deadline": "事件發生後24小時內通報",
        "required_documents": ["產品檢驗報告", "庫存盤點紀錄", "供應商來源資料", "消費者申訴紀錄", "內部改善報告"],
        "penalties": "罰鍰新台幣6萬至2億元，情節重大者得命其歇業",
    },
    "hygiene": {
        "reporting_authority": "地方衛生局",
        "deadline": "限期改善通知後依指定期限",
        "required_documents": ["清潔消毒紀錄", "病媒防治報告", "員工健康檢查證明", "環境檢測報告"],
        "penalties": "罰鍰新台幣6萬至2億元",
    },
    "data_breach": {
        "reporting_authority": "個人資料保護委員會(籌備處) / 數位發展部",
        "deadline": "事件發生後72小時內通報",
        "required_documents": ["資料外洩影響範圍說明", "已採取的補救措施", "通知當事人之紀錄", "後續防止措施計畫"],
        "penalties": "罰鍰新台幣2萬至20萬元(按次處罰)，損害賠償最高2億元",
    },
    "labor_violation": {
        "reporting_authority": "地方勞工局 / 勞動部",
        "deadline": "依勞動檢查結果通知限期改善",
        "required_documents": ["出勤紀錄", "薪資明細", "勞工名卡", "勞健保投保紀錄"],
        "penalties": "罰鍰新台幣2萬至100萬元，並得公布事業單位名稱",
    },
}

EVIDENCE_PRESERVATION_GUIDE = {
    "general": [
        "保存所有相關文件、通聯記錄、監視器畫面",
        "建立事件時間軸，記錄每個關鍵事件發生的時間與內容",
        "蒐集並保存所有顧客投訴的原始內容與回應紀錄",
        "拍照或錄影記錄現場狀況（如有實體據點）",
        "保存供應商合約、進貨單據、檢驗報告等文件",
        "建立內部事件調查報告，記錄事發經過與處理過程",
    ],
    "social_media": [
        "截圖保存所有相關社群媒體貼文與留言（包含時間戳記）",
        "記錄貼文分享數、留言數、按讚/心情數等傳播數據",
        "保存所有官方回應的內容與時間",
        "記錄不實資訊的來源帳號與散布路徑",
        "如有惡意攻擊，保存IP位置、帳號資訊等數位證據",
    ],
}

RISK_ASSESSMENT_MATRIX = {
    "defamation": {
        "risk_level": "中等至高度",
        "trigger_conditions": [
            "社群媒體上出現不實指控或負面影射",
            "媒體報導內容對商譽造成實質損害",
            "競爭對手散布不實資訊",
            "離職員工或消費者公開發表負面陳述",
        ],
        "legal_options": [
            "發送存證信函要求澄清或道歉",
            "向檢察官提起刑事妨害名譽告訴",
            "民事訴訟請求損害賠償與回復名譽",
            "聲請假處分禁止繼續散布",
        ],
    },
    "consumer_dispute": {
        "risk_level": "低至中等",
        "trigger_conditions": [
            "消費者對產品或服務品質提出申訴",
            "退費/退款爭議",
            "廣告內容引發誤解",
            "契約條款爭議",
        ],
        "legal_options": [
            "優先以協商和解方式處理",
            "函請消保官調解",
            "訴訟前應評估法律成本與商譽影響",
            "改善定型化契約條款以符合法規",
        ],
    },
}


class LegalAgent(BaseAgent):
    """Legal AI Agent for compliance risk analysis and legal advisory generation."""

    def __init__(self, name: str = "LegalAgent", description: str = "Legal compliance and risk advisory agent", model_tier: str = "PRO"):
        super().__init__(name, description, model_tier)

    async def analyze(self, context: Dict) -> Dict:
        """Analyze legal risks from incident context."""
        self.log_call()
        incident_type = context.get("incident_type", "general")
        voices = context.get("voices", [])
        incident_detail = context.get("incident_detail", {})

        legal_risks = self._assess_legal_risks(incident_type, voices)
        compliance_status = self._check_compliance(incident_type, context)
        evidence_steps = self._get_evidence_steps(incident_type, voices)
        regulatory_requirements = REGULATORY_REQUIREMENTS.get(incident_type, {})

        analysis = {
            "incident_type": incident_type,
            "legal_risks": legal_risks,
            "compliance_status": compliance_status,
            "evidence_preservation_steps": evidence_steps,
            "regulatory_requirements": regulatory_requirements,
            "overall_legal_risk_score": self._calculate_legal_risk_score(legal_risks),
            "legal_advisory": self.generate_legal_advisory(incident_type),
            "timestamp": datetime.now().isoformat(),
        }

        self.remember("last_legal_analysis", analysis)
        return analysis

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate legal compliance recommendations."""
        self.log_call()
        recommendations = []
        risks = analysis.get("legal_risks", {})
        compliance = analysis.get("compliance_status", {})

        for risk_area, risk_data in risks.items():
            if risk_data.get("level") in ("high", "critical"):
                recommendations.append({
                    "priority": "CRITICAL",
                    "category": "legal_risk_mitigation",
                    "area": risk_area,
                    "action": f"優先處理{risk_area}法律風險",
                    "detail": f"風險等級: {risk_data['level']}。{risk_data.get('description', '')}",
                    "legal_advisory": risk_data.get("advisory", ""),
                })

        for item in compliance.get("missing_items", []):
            recommendations.append({
                "priority": "HIGH",
                "category": "compliance",
                "action": f"補足合規項目: {item}",
                "detail": f"此項目為法規要求之必要文件或程序，建議立即準備",
            })

        if analysis.get("regulatory_requirements"):
            req = analysis["regulatory_requirements"]
            recommendations.append({
                "priority": "HIGH",
                "category": "regulatory_reporting",
                "action": f"向{req.get('reporting_authority', '主管機關')}進行通報",
                "detail": f"法規要求應於{req.get('deadline', '期限內')}完成通報",
                "required_documents": req.get("required_documents", []),
            })

        evidence_steps = analysis.get("evidence_preservation_steps", [])
        if evidence_steps:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "evidence",
                "action": "啟動證據保全程序",
                "detail": "; ".join(evidence_steps[:5]),
            })

        self.remember("last_legal_recommendations", recommendations)
        return recommendations

    def generate_legal_advisory(self, incident_type: str) -> Dict:
        """Generate legal guidance based on incident type."""
        self.log_call()

        advisories = {
            "food_safety": {
                "title": "食品安全事件法律諮詢意見",
                "summary": "本案涉及食品安全衛生管理法相關規定，須立即採取以下法律行動以降低法律風險。",
                "immediate_actions": [
                    "立即暫停販售問題產品，啟動自主召回程序",
                    "於24小時內向轄區衛生局通報",
                    "保存產品樣本及相關檢驗紀錄",
                    "通知下游業者停止使用或販售",
                    "準備消費者申訴處理機制",
                ],
                "risk_mitigation": [
                    "委請第三方公正檢驗機構進行產品檢驗",
                    "檢視產品責任保險是否足以涵蓋本次事件",
                    "準備損害賠償預備金",
                    "委任專業律師協助處理後續法律程序",
                ],
                "key_legislation": [
                    "食品安全衛生管理法第7條(自主管理義務)",
                    "食品安全衛生管理法第15條(食品不得製造、加工、販賣之情形)",
                    "食品安全衛生管理法第44條(罰則)",
                    "消費者保護法第7條(商品製造人責任)",
                ],
            },
            "hygiene": {
                "title": "衛生違規事件法律諮詢意見",
                "summary": "本案涉及食品良好衛生規範(GHP)及相關衛生法規，應立即進行衛生改善並配合主管機關稽查。",
                "immediate_actions": [
                    "立即進行全面清潔消毒作業",
                    "檢視並更新衛生管理制度文件",
                    "安排員工健康檢查",
                    "委請病媒防治專業公司進行處理",
                    "準備衛生稽查應對文件",
                ],
                "risk_mitigation": [
                    "建立每日衛生檢查紀錄表",
                    "導入食品安全管制系統(HACCP)",
                    "定期委託第三方進行衛生稽核",
                    "加強員工衛生教育訓練",
                ],
                "key_legislation": [
                    "食品安全衛生管理法第8條(食品良好衛生規範)",
                    "食品良好衛生規範準則(GHP)",
                    "食品安全衛生管理法第44條(罰則)",
                ],
            },
            "data_privacy": {
                "title": "個人資料外洩事件法律諮詢意見",
                "summary": "本案涉及個人資料保護法，須於72小時內完成通報並採取補救措施。",
                "immediate_actions": [
                    "立即啟動資安事件應變程序",
                    "查明外洩範圍與影響人數",
                    "於72小時內通報主管機關",
                    "通知受影響之當事人",
                    "採取必要補救措施防止損害擴大",
                ],
                "risk_mitigation": [
                    "強化資訊安全管理制度",
                    "導入個資去識別化技術",
                    "定期進行資安檢測與滲透測試",
                    "檢視並更新個資保護政策",
                ],
                "key_legislation": [
                    "個人資料保護法第12條(事故通報)",
                    "個人資料保護法第27條(安全維護措施)",
                    "個人資料保護法第48條(罰則)",
                ],
            },
            "labor": {
                "title": "勞動法規事件法律諮詢意見",
                "summary": "本案涉及勞動基準法相關規定，應立即檢視勞動條件是否符合法規要求。",
                "immediate_actions": [
                    "檢視員工出勤紀錄與薪資明細",
                    "確認加班費計算是否符合規定",
                    "檢查休假安排是否合法",
                    "確保勞健保投保級距正確",
                ],
                "risk_mitigation": [
                    "導入勞動法遵稽核制度",
                    "定期舉辦勞動法規教育訓練",
                    "聘請專業勞務顧問定期檢視制度",
                    "建立勞資溝通管道",
                ],
                "key_legislation": [
                    "勞動基準法第24條(延長工時工資)",
                    "勞動基準法第36條(例假與休息日)",
                    "勞動基準法第79條(罰則)",
                ],
            },
            "defamation": {
                "title": "商譽損害事件法律諮詢意見",
                "summary": "本案涉及不實資訊散布可能構成妨害名譽，需評估法律救濟途徑。",
                "immediate_actions": [
                    "全面蒐集並保存不實資訊內容與散布證據",
                    "評估資訊內容是否構成誹謗",
                    "發出澄清聲明以正視聽",
                    "必要時發送存證信函要求下架與道歉",
                ],
                "risk_mitigation": [
                    "建立網路輿情監控機制",
                    "建立危機公關標準作業流程",
                    "定期法律風險評估",
                ],
                "key_legislation": [
                    "刑法第310條(誹謗罪)",
                    "刑法第313條(妨害信用罪)",
                    "民法第195條(名譽權侵害)",
                    "公平交易法第24條(營業信譽)",
                ],
            },
            "consumer_protection": {
                "title": "消費者爭議事件法律諮詢意見",
                "summary": "本案涉及消費者保護法相關規定，建議優先以協商方式解決爭議。",
                "immediate_actions": [
                    "主動聯繫消費者了解訴求",
                    "評估退費/換貨/賠償方案",
                    "記錄所有溝通內容與時間",
                    "檢視定型化契約條款符合性",
                ],
                "risk_mitigation": [
                    "建立消費者爭議處理SOP",
                    "定期檢視服務條款公平性",
                    "強化第一線人員消保法教育訓練",
                ],
                "key_legislation": [
                    "消費者保護法第7條(商品責任)",
                    "消費者保護法第11條(定型化契約)",
                    "消費者保護法第51條(懲罰性賠償)",
                ],
            },
        }

        return advisories.get(incident_type, {
            "title": "一般法律諮詢意見",
            "summary": "本案涉及一般法律風險，建議進行全面法律評估。",
            "immediate_actions": [
                "全面搜集相關事證與文件",
                "諮詢專業律師進行法律風險評估",
                "保存所有相關通聯紀錄與文件",
            ],
            "risk_mitigation": [
                "建立法遵管理機制",
                "定期法律風險評估",
            ],
            "key_legislation": [],
        })

    def check_compliance(self, statement: str) -> Dict:
        """Review a PR statement for legal compliance risks."""
        self.log_call()
        risks = []
        warnings = []

        high_risk_phrases = {
            "保證": "避免使用絕對性保證用語，可能構成廣告不實或契約責任",
            "絕對": "絕對性用語可能引發消費爭議",
            "100%": "數值宣稱需有科學證據支持，否則可能構成不實廣告",
            "永遠": "時間性保證用語風險極高",
            "一定": "保證性用語應謹慎使用",
            "絕不": "強烈否定用語可能限制未來彈性",
            "從未": "歷史性否定陳述需有確切證據",
            "所有": "概括性用語可能涉及不實陳述",
            "唯一": "獨特性宣稱可能涉及公平交易法",
            "第一": "排名宣稱需有客觀數據支持",
        }

        for phrase, warning in high_risk_phrases.items():
            if phrase in statement:
                risks.append({"phrase": phrase, "risk": warning, "severity": "medium"})
                warnings.append(f"「{phrase}」: {warning}")

        liability_phrases = {
            "賠償": "若明確承諾賠償金額或範圍，將構成法律義務",
            "全額退費": "無條件退費承諾可能導致大量退費請求",
            "無條件": "無條件承諾限縮了未來協商空間",
            "負全責": "責任範圍陳述可能影響法律責任認定",
            "承認": "承認用語可能被視為法律上的自認",
        }

        for phrase, warning in liability_phrases.items():
            if phrase in statement:
                risks.append({"phrase": phrase, "risk": warning, "severity": "high"})
                warnings.append(f"「{phrase}」: {warning}")

        compliance_score = max(100 - len(risks) * 10, 0)

        return {
            "compliance_score": compliance_score,
            "risk_level": "high" if len(risks) >= 5 else ("medium" if len(risks) >= 2 else "low"),
            "risks_found": risks,
            "warnings": warnings,
            "recommendation": (
                "建議重新檢視並修改上述高風險用語後再行發布，並由法務單位進行最終審查。"
                if len(risks) > 0
                else "聲明內容目前未發現重大法律風險，建議仍由法務單位進行最終確認。"
            ),
        }

    def _assess_legal_risks(self, incident_type: str, voices: List[Dict]) -> Dict:
        risks = {}
        all_text = " ".join([v.get("content", "") + v.get("title", "") for v in voices])

        defamation_kw = ["說謊", "騙", "黑心", "坑", "詐騙", "不實", "做假"]
        labor_kw = ["過勞", "加班", "薪水", "薪資", "工時", "勞工", "派遣", "沒勞健保"]
        consumer_kw = ["退費", "退款", "退錢", "賠", "申訴", "消保", "消費糾紛"]
        privacy_kw = ["個資", "洩漏", "電話外流", "資料", "未經同意"]
        food_kw = ["中毒", "腹瀉", "過期", "發霉"]

        if incident_type == "defamation" or any(kw in all_text for kw in defamation_kw):
            risks["defamation"] = {
                "level": "high" if sum(1 for kw in defamation_kw if kw in all_text) >= 3 else "medium",
                "description": "社群媒體上存在可能構成誹謗的不實資訊流傳",
                "advisory": "蒐集證據，評估是否採取法律行動",
            }

        if incident_type == "labor" or any(kw in all_text for kw in labor_kw):
            risks["labor"] = {
                "level": "high" if sum(1 for kw in labor_kw if kw in all_text) >= 3 else "medium",
                "description": "可能存在勞動法規遵循疑慮",
                "advisory": "立即檢視勞動條件是否符合法規",
            }

        if incident_type == "consumer_protection" or any(kw in all_text for kw in consumer_kw):
            risks["consumer_protection"] = {
                "level": "medium",
                "description": "消費者爭議有擴大趨勢",
                "advisory": "優先以協商方式解決，必要時函請消保官調解",
            }

        if any(kw in all_text for kw in privacy_kw):
            risks["data_privacy"] = {
                "level": "high",
                "description": "存在個人資料保護疑慮",
                "advisory": "立即啟動個資事件應變程序，查明外洩範圍",
            }

        if incident_type in ("food_safety", "hygiene") or any(kw in all_text for kw in food_kw):
            risks["food_safety"] = {
                "level": "critical",
                "description": "涉及食品安全衛生管理法相關風險",
                "advisory": "立即通報衛生主管機關並啟動產品召回程序",
            }

        return risks

    def _check_compliance(self, incident_type: str, context: Dict) -> Dict:
        checklist = COMPLIANCE_CHECKLIST.get(incident_type, [])
        available_docs = context.get("available_documents", [])

        missing_items = [item for item in checklist if not any(doc in item for doc in available_docs)]
        compliance_rate = round((len(checklist) - len(missing_items)) / max(len(checklist), 1) * 100, 1)

        return {
            "checklist_total": len(checklist),
            "missing_items": missing_items,
            "compliant_items": [i for i in checklist if i not in missing_items],
            "compliance_rate": compliance_rate,
            "status": "compliant" if compliance_rate >= 80 else ("partial" if compliance_rate >= 50 else "non_compliant"),
        }

    def _get_evidence_steps(self, incident_type: str, voices: List[Dict]) -> List[str]:
        steps = list(EVIDENCE_PRESERVATION_GUIDE["general"])

        has_social = any(v.get("channel") in ("facebook", "ptt", "threads", "google_review") for v in voices)
        if has_social:
            steps.extend(EVIDENCE_PRESERVATION_GUIDE["social_media"])

        return steps

    def _calculate_legal_risk_score(self, risks: Dict) -> Dict:
        level_weights = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        total_weight = sum(level_weights.get(r["level"], 0) for r in risks.values())
        max_possible = len(risks) * 10 or 1
        normalized = round(total_weight / max_possible * 100, 1)

        if normalized >= 70:
            level = "critical"
        elif normalized >= 40:
            level = "high"
        elif normalized >= 20:
            level = "medium"
        else:
            level = "low"

        return {"score": normalized, "level": level, "risk_areas_count": len(risks)}
