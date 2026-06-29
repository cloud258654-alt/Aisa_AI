var MockData = (function () {
  var reviewBank = [
    {
      channel: 'google', channelName: 'Google Maps 評論', author: '張*豪',
      text: '這家信義店的服務態度真的很不ok，點完餐等了30分鐘才說漏單，最後送上來的牛排還是溫冷的...真的不會再來第二次了。',
      sentiment: 'negative', emotion: 'Anger 😠', topic: '服務態度 / 出餐速度', store: '信義旗艦店', risk: 'mid'
    },
    {
      channel: 'threads', channelName: 'Threads', author: 'charlie_daily',
      text: '剛剛在忠孝店吃飯，隔壁桌的客人居然為了排隊順序跟店員大吵，店長處理速度很快，主動送了兩張折價券把人安撫走，危機處理給過！👍',
      sentiment: 'positive', emotion: 'Delight 😄', topic: '客訴處理', store: '忠孝 SOGO 店', risk: 'low'
    },
    {
      channel: 'ptt', channelName: 'PTT Food 版', author: 'windrider',
      text: '[食記] 台中公益店新菜單體驗！極黑和牛拼盤份量很多，肉質很棒，服務人員烤肉技巧很好，雖然價格偏高但非常推薦家庭聚餐。',
      sentiment: 'positive', emotion: 'Trust 🤝', topic: '食材品質 / 服務體驗', store: '台中公益店', risk: 'low'
    },
    {
      channel: 'facebook', channelName: 'Facebook Page', author: '林秀琴',
      text: '打電話去預約板橋店，接電話的服務生態度愛理不理的，問他有沒有包廂也講不清楚，到底有沒有受過員工訓練啊？',
      sentiment: 'negative', emotion: 'Frustration 😩', topic: '預約系統 / 員工訓練', store: '板橋大遠百店', risk: 'mid'
    },
    {
      channel: 'instagram', channelName: 'Instagram Tag', author: 'yuki_travel',
      text: '新裝潢的信義旗艦店超美！霓虹燈區隨便拍都超有質感，點了限定的芒果聖代也很好吃，大推週末跟閨蜜一起來約會打卡📸✨',
      sentiment: 'positive', emotion: 'Joy 😊', topic: '店面裝潢 / 甜點品質', store: '信義旗艦店', risk: 'low'
    },
    {
      channel: 'dcard', channelName: 'Dcard 美食板', author: '逢甲小食神',
      text: '有人吃過這家的台中公益店嗎？聽說最近尖峰時間排隊要等快兩個小時，不知道值不值得排？還是有推薦比較不擠的時段？',
      sentiment: 'neutral', emotion: 'Curiosity 🤔', topic: '候位時間', store: '台中公益店', risk: 'low'
    },
    {
      channel: 'google', channelName: 'Google Maps 評論', author: 'Elena Wang',
      text: '今天去用餐，點餐APP一直當機跑不出條碼，結帳的櫃檯只有開一個，大排長龍，希望可以儘快更新系統。',
      sentiment: 'negative', emotion: 'Frustration 😩', topic: '硬體系統 / 結帳流程', store: '信義旗艦店', risk: 'low'
    },
    {
      channel: 'threads', channelName: 'Threads', author: 'jessica_w',
      text: '笑死，這家台北店又被爆出服務生臉很臭，但我每次去都覺得還好耶？果然評論都看看就好，還是自己吃過最準。',
      sentiment: 'neutral', emotion: 'Neutral 😐', topic: '服務態度', store: '信義旗艦店', risk: 'low'
    }
  ];

  var authorPool = ['陳*美', '王*明', 'Li_99', 'abby_c', 'justin_t', '吳*華'];

  var presetCrises = {
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
        rootCause: '<div class="analysis-summary-block"><span class="analysis-headline">Threads 食安謠言 - 原因追蹤</span><div class="analysis-points"><div class="analysis-point-item"><strong>輿情源頭</strong> Threads 網友 @yummy_test 發文指稱「吃完回家拉肚子」，引發 150+ 轉發。</div><div class="analysis-point-item"><strong>內部數據</strong> 當日信義店食材留樣紀錄良好，冰箱溫度監控正常，但「海鮮送達至出餐」流程在尖峰段有 12 分鐘的室溫曝露空檔。</div><div class="analysis-point-item"><strong>診斷結論</strong> 雖無明確食物中毒科學證據，但出餐流暢度不足導致的餐點失溫，是造成顧客口感不佳與懷疑的主因。</div></div></div>',
        sop: '<ul class="sop-checklist"><li class="sop-item"><input type="checkbox" id="t-sop-1"> <span>信義店海鮮食材改為「出餐前最後一刻自冷藏庫取出」，嚴禁提前置於室溫備餐。</span></li><li class="sop-item"><input type="checkbox" id="t-sop-2"> <span>店經理主動聯絡原貼文網友，詢問就醫證明並承諾全額負擔醫療費用，展現積極負責態度。</span></li><li class="sop-item"><input type="checkbox" id="t-sop-3"> <span>召回當天庫存食材，委託第三方公正機構進行自主檢驗 (大腸桿菌群、沙門氏菌)。</span></li></ul>',
        pr: '<div class="pr-block" id="pr-statement-text-t">【品牌官方聲明】\n針對今日網路社群提及信義店食材安全之疑慮，本公司高度重視。\n本公司已於第一時間對信義店進行全面自主清查，當日冰箱溫度、人員衛生及留樣紀錄均符合標準。目前已主動聯繫發文顧客了解身體狀況，並同步將同批食材送往第三方檢驗。\n我們深知食品安全為企業命脈，後續檢驗結果將公開透明說明。若同仁出餐速度與溫度有未達標準之處，我們深表歉意，並已啟動流程優化。</div><div class="pr-actions"><button class="btn btn-secondary btn-copy-pr" data-target="pr-statement-text-t">複製聲明</button><button class="btn btn-primary btn-publish-pr" data-type="Threads">一鍵張貼至 Threads</button></div>',
        legal: '<div class="legal-grid"><div class="legal-box alert"><h4>法務防線警示</h4><ul><li>保留當日發文截圖與後續傳播鏈，若證實屬同行惡意造謠，可依民法妨礙商譽求償。</li><li>聲明中切勿承諾「賠償一定金額」，需註明「協助釐清身體狀況及支付合理醫療費用」。</li></ul></div><div class="legal-box training"><h4>門市再培訓要點</h4><ul><li>全體外場加強「異常餐點回收通報機制」，若顧客反應海鮮有異味，應立即撤餐並通報主管。</li><li>廚房幹部加強「冷鏈交接時間控管」教育訓練。</li></ul></div></div>'
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
        rootCause: '<div class="analysis-summary-block"><span class="analysis-headline">Google 排隊糾紛 - 原因追蹤</span><div class="analysis-points"><div class="analysis-point-item"><strong>輿情源頭</strong> 顧客投訴現場服務生「沒發號碼牌，讓後來的人先入座」，造成插隊誤會，引發多組顧客跟進洗負評。</div><div class="analysis-point-item"><strong>內部數據</strong> 當天信義店實施「APP與現場混合候位」，由於條碼掃描器故障，帶位同仁改採人工登記，因名單重疊導致順序出錯。</div><div class="analysis-point-item"><strong>診斷結論</strong> 軟硬體配套備援不足，加上尖峰時段現場無專門的排隊動線指引牌，導致顧客觀感極差。</div></div></div>',
        sop: '<ul class="sop-checklist"><li class="sop-item"><input type="checkbox" id="g-sop-1"> <span>立即購置「實體紅龍排隊指引」，清楚區分「APP已報到區」與「現場登記區」。</span></li><li class="sop-item"><input type="checkbox" id="g-sop-2"> <span>當候位系統當機時，強制執行「三聯單手寫登記」，並主動向排隊顧客說明規則。</span></li><li class="sop-item"><input type="checkbox" id="g-sop-3"> <span>針對當場受排隊糾紛波及的顧客，由店長代表致歉並贈送茶點兌換券。</span></li></ul>',
        pr: '<div class="pr-block" id="pr-statement-text-g">親愛的顧客您好，對於今日信義店現場排隊動線引導不佳、造成您用餐心情受影響，我們致上最深的歉意。\n由於當天候位系統偶發故障，同仁切換手工作業時順序有誤，導致您的權益受損。我們已重新規劃現場紅龍指引與備援登記流程，並對當天帶位同仁加強現場溝通培訓。\n我們非常希望能有機會聯絡您，提供後續補償，您的建議是我們持續進步的動力。</div><div class="pr-actions"><button class="btn btn-secondary btn-copy-pr" data-target="pr-statement-text-g">複製聲明</button><button class="btn btn-primary btn-publish-pr" data-type="Google">張貼回覆至 Google Review</button></div>',
        legal: '<div class="legal-grid"><div class="legal-box alert"><h4>法務防線警示</h4><ul><li>注意員工個資保護，現場糾紛中若顧客拍攝店員臉部並威脅公審，應由店長出面提醒不可散佈肖像。</li><li>提醒員工切勿在網路上使用私人帳號與顧客筆戰，避免火上加油。</li></ul></div><div class="legal-box training"><h4>門市再培訓要點</h4><ul><li>帶位同仁必須學會「系統故障備援三部曲」口訣，並保持語氣溫和堅定。</li><li>尖峰時段加派一名店副理在門口進行情緒安撫與人流疏導。</li></ul></div></div>'
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
        rootCause: '<div class="analysis-summary-block"><span class="analysis-headline">PTT 態度爆料 - 原因追蹤</span><div class="analysis-points"><div class="analysis-point-item"><strong>輿情源頭</strong> PTT 網友發文公審「結帳員臉臭、找零錢用丟的」，引發鄉民熱議「服務業態度差」。</div><div class="analysis-point-item"><strong>內部數據</strong> 當事員工 A 為工讀生，當週已排班 46 小時，且該時段經歷了連續 3 小時的收銀高峰，無替補休息。</div><div class="analysis-point-item"><strong>診斷結論</strong> 雖拋接零錢純屬疲憊手滑之誤會，但人員排班超時、櫃檯站點過久造成的生理與心理疲憊，是服務熱忱下降的根本原因。</div></div></div>',
        sop: '<ul class="sop-checklist"><li class="sop-item"><input type="checkbox" id="p-sop-1"> <span>店經理約談該員工進行關懷，若有排班過重情況，立即調整排班時段，並調離收銀第一線。</span></li><li class="sop-item"><input type="checkbox" id="p-sop-2"> <span>增設「收銀限時輪值機制」，單人連續收銀時間不得超過 2 小時。</span></li><li class="sop-item"><input type="checkbox" id="p-sop-3"> <span>向發文顧客發送致歉私訊，解釋因疲憊手滑之誤會，並承諾改進人員調度。</span></li></ul>',
        pr: '<div class="pr-block" id="pr-statement-text-p">您好，針對今日 PTT 論壇提及信義店結帳服務不佳的事件，本公司深感遺憾與抱歉。\n經內部查核，當下因收銀尖峰時段同仁操作疲憊、找零時手滑造成您的誤解。我們已於第一時間對該位同仁進行關懷晤談，並檢討門市的排班工時與收銀輪替機制，避免人員過度疲勞影響服務品質。\n我們將持續落實溫暖、尊重的服務規範，感謝您的回饋，讓我們有修正與改進的機會。</div><div class="pr-actions"><button class="btn btn-secondary btn-copy-pr" data-target="pr-statement-text-p">複製聲明</button><button class="btn btn-primary btn-publish-pr" data-type="PTT">回信致歉 PTT 網友</button></div>',
        legal: '<div class="legal-grid"><div class="legal-box alert"><h4>法務防線警示</h4><ul><li>注意勞基法工時上限，避免兼職同仁每週總工時超過規範，引發勞檢風險。</li><li>避免將員工個人姓名、照片流出至網路，保護員工隱私，避免引起內部反彈。</li></ul></div><div class="legal-box training"><h4>門市再培訓要點</h4><ul><li>結帳「雙手找零與收付」標準動作再宣導，防止因快速投遞造成拋擲誤會。</li><li>店經理加強觀察現場同仁精神狀態，彈性調整後台休息時間。</li></ul></div></div>'
      }
    }
  };

  return {
    reviewBank: reviewBank,
    authorPool: authorPool,
    presetCrises: presetCrises
  };
})();
